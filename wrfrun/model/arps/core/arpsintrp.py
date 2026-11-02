"""
ARPS interpolation executable.

.. autosummary::
    :toctree: generated/

    ARPSIntrp
"""

import logging
import re
from dataclasses import asdict

from wrfrun.core import WRFRUN, ExecutableBase, ResourceRef, ResultSource

from ._common import prepare_component_namelist

LOGGER = logging.getLogger("wrfrun")


class ARPSIntrp(ExecutableBase):
    """Create external ARPS boundary data from staged history files."""

    def __init__(
        self,
        history_source: ResultSource | None = None,
        core_num: int | None = None,
    ):
        """Create an ``arpsintrp`` executable and select its history source."""
        if core_num is None or core_num == 1:
            cmd = "./arpsintrp"
            work_path = ResourceRef("workspace_arps", "arpsintrp")
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = None
            LOGGER.info("Use serial arpsintrp.")
        else:
            cmd = "./arpsintrp_mpi"
            work_path = ResourceRef("workspace_arps", "arpsintrp_mpi")
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num
            LOGGER.info("Use parallel arpsintrp.")

        self.namelist_path = work_path / "arpsintrp.nml"

        super().__init__(
            name="arpsintrp",
            cmd=cmd,
            work_path=work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        self.history_source = history_source
        prepare_component_namelist("arpsintrp")

    def generate_custom_config(self):
        """Store the selected history source and namelist for replay."""
        self.custom_config.update(
            {
                "history_source": asdict(self.history_source) if self.history_source is not None else None,
                "namelist": WRFRUN.namelist.get_namelist("arpsintrp"),
            }
        )

    def load_custom_config(self):
        """Restore the selected history source and namelist for replay."""
        if not WRFRUN.namelist.check_namelist_id("arpsintrp"):
            WRFRUN.namelist.register_namelist_id("arpsintrp")
        history_source = self.custom_config["history_source"]
        self.history_source = ResultSource(**history_source) if history_source is not None else None
        WRFRUN.namelist.update_namelist(self.custom_config["namelist"], "arpsintrp")

    def _stage_history_data(self):
        """Stage history inputs and write their runtime namelist paths."""
        if self.history_source is not None:
            input_ref = WRFRUN.resource.get_result_ref(source=self.history_source)

        else:
            input_ref = WRFRUN.resource.INPUT_DIR / "arpsintrp"

        input_files = list(WRFRUN.resource.get_custom_resource(input_ref).iterdir())
        grid_base_file = next(file for file in input_files if re.fullmatch(r".+\.(?:hdf|h5f)grdbas", file.name))
        history_files = sorted(file for file in input_files if re.fullmatch(r".+\.(?:hdf|h5f)\d{6}", file.name))

        self.add_input_files([input_ref / file.name for file in [grid_base_file, *history_files]])
        WRFRUN.namelist.update_namelist(
            {
                "history_data": {
                    "hdmpinopt": 2,
                    "grdbasfn": f"./{grid_base_file.name}",
                    "nhisfile": len(history_files),
                    "hisfile": [f"./{file.name}" for file in history_files],
                }
            },
            "arpsintrp",
        )

    def before_exec(self):
        """Stage history data and write the ARPSIntrp namelist."""
        WRFRUN.states.check_wrfrun_context(True)
        WRFRUN.states.WRFRUN_WORK_STATUS = "arpsintrp"
        WRFRUN.resource.mkdir(self.work_path / "outputs")
        self._stage_history_data()
        WRFRUN.namelist.update_namelist({"jobname": {"runname": self.name}, "output": {"dirname": "./outputs/"}}, "arpsintrp")
        WRFRUN.namelist.write_namelist(self.namelist_path, "arpsintrp")
        super().before_exec()

    def after_exec(self):
        """Archive generated boundary data and the runtime namelist."""
        if not WRFRUN.states.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )
            self.add_output_files(
                filenames="arpsintrp.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


__all__ = ["ARPSIntrp"]
