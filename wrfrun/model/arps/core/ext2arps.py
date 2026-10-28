"""
ARPS external-data conversion executable.

.. autosummary::
    :toctree: generated/

    EXT2ARPS
"""

import glob
import logging
from datetime import datetime, timedelta
from os.path import exists

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from ._common import check_and_prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


def _check_ext2arps_input_data() -> list[str]:
    """Return external-data filenames required by the current ARPS namelist."""
    data_input_dir = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.INPUT_DIR / "ext2arps")
    namelist = WRFRUN_NEW.namelist.get_namelist("arps")
    extdname = namelist["extdfile"]["extdname"]
    nextdfil = namelist["extdfile"]["nextdfil"]
    extdtime = namelist["extdfile"]["extdtime"]

    if isinstance(extdtime, str):
        extdtime = [extdtime]

    if len(extdtime) < nextdfil:
        message = f"Expected {nextdfil} values in 'extdtime', but only got {len(extdtime)}."
        LOGGER.error(message)
        raise ValueError(message)

    expected_files: list[str] = []
    missing_files: list[str] = []
    for time_string in extdtime[:nextdfil]:
        try:
            initial_time_string, forecast_time_string = time_string.split("+", maxsplit=1)
            initial_time = datetime.strptime(initial_time_string, "%Y-%m-%d.%H:%M:%S")
        except ValueError as exc:
            LOGGER.error(f"Invalid extdtime setting: '{time_string}'")
            raise ValueError(f"Invalid extdtime setting: '{time_string}'") from exc

        try:
            hour_str, minute_str, second_str = forecast_time_string.split(":")
            forecast_time = timedelta(hours=int(hour_str), minutes=int(minute_str), seconds=int(second_str))
        except ValueError as exc:
            LOGGER.error(f"Invalid forecast offset in extdtime: '{time_string}'")
            raise ValueError(f"Invalid forecast offset in extdtime: '{time_string}'") from exc

        filename = f"{extdname}.{initial_time.strftime('%Y%m%d%H')}f{int(forecast_time.total_seconds() // 3600):02d}"
        expected_files.append(filename)
        if not exists(f"{data_input_dir}/{filename}"):
            missing_files.append(filename)

    if missing_files:
        message = f"Can't find required ext2arps input files in '{data_input_dir}': {', '.join(missing_files)}"
        LOGGER.error(message)
        raise FileNotFoundError(message)

    return expected_files


class EXT2ARPS(ExecutableBase):
    """Convert external fields into ARPS initial and boundary data."""

    def __init__(self, arpstrn_run_id: str | None = None):
        """Create an ``ext2arps`` executable."""
        work_path = ResourceRef("workspace_arps", "ext2arps")
        self.namelist_path = work_path / "ext2arps.nml"

        super().__init__(
            name="ext2arps",
            cmd="./ext2arps",
            work_path=work_path,
            stdin_file=self.namelist_path,
        )

        self.arpstrn_run_id = arpstrn_run_id
        check_and_prepare_arps_namelist()

    def generate_custom_config(self):
        """Store the selected terrain run and ARPS namelist for replay."""
        self.custom_config.update({"arpstrn_run_id": self.arpstrn_run_id, "namelist": WRFRUN_NEW.namelist.get_namelist("arps")})

    def load_custom_config(self):
        """Restore the selected terrain run and ARPS namelist for replay."""
        self.arpstrn_run_id = self.custom_config["arpstrn_run_id"]
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "ext2arps"
        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        input_files = _check_ext2arps_input_data()
        self.add_input_files([WRFRUN_NEW.resource.INPUT_DIR / "ext2arps" / name for name in input_files])

        terrain_ref = WRFRUN_NEW.resource.get_result_ref("arpstrn", self.arpstrn_run_id)
        terrain_dir = WRFRUN_NEW.resource.get_custom_resource(terrain_ref)
        terrain_files = glob.glob("arpstrn.trndata*", root_dir=terrain_dir)
        if not terrain_files:
            message = "Can't find arpstrn outputs in ext2arps outputs directory, which is essential to run ext2arps."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        terrain_file = terrain_ref / terrain_files[0]
        self.add_input_files(terrain_file, is_output=False)
        WRFRUN_NEW.namelist.update_namelist(
            {
                "jobname": {"runname": self.name},
                "terrain": {"terndta": f"./{terrain_file.name}"},
                "extdfile": {"dir_extd": "./", "grdbasopt": 1},
            },
            "arps",
        )
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )
            self.add_output_files(
                filenames="ext2arps.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


__all__ = ["EXT2ARPS"]
