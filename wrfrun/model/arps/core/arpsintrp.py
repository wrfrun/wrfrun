"""
ARPS interpolation executable.

.. autosummary::
    :toctree: generated/

    ARPSIntrp
"""

import re

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from ._common import prepare_component_namelist


class ARPSIntrp(ExecutableBase):
    """Create external ARPS boundary data from staged history files."""

    def __init__(self, history_executable: str | None = None, history_run_id: str | None = None):
        """Create an ``arpsintrp`` executable and select its history source."""
        work_path = ResourceRef("workspace_arps", "arpsintrp")
        self.namelist_path = work_path / "arpsintrp.nml"
        super().__init__(
            name="arpsintrp",
            cmd="./arpsintrp",
            work_path=work_path,
            stdin_file=self.namelist_path,
        )

        self.history_executable = history_executable
        self.history_run_id = history_run_id
        prepare_component_namelist("arpsintrp")

    def generate_custom_config(self):
        """Store the selected history source and namelist for replay."""
        self.custom_config.update(
            {
                "history_executable": self.history_executable,
                "history_run_id": self.history_run_id,
                "namelist": WRFRUN_NEW.namelist.get_namelist("arpsintrp"),
            }
        )

    def load_custom_config(self):
        """Restore the selected history source and namelist for replay."""
        if not WRFRUN_NEW.namelist.check_namelist_id("arpsintrp"):
            WRFRUN_NEW.namelist.register_namelist_id("arpsintrp")
        self.history_executable = self.custom_config["history_executable"]
        self.history_run_id = self.custom_config["history_run_id"]
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arpsintrp")

    def _stage_history_data(self):
        """Stage history inputs and write their runtime namelist paths."""
        if self.history_executable is not None:
            input_ref = WRFRUN_NEW.resource.get_result_ref(self.history_executable, self.history_run_id)

        else:
            input_ref = WRFRUN_NEW.resource.INPUT_DIR / "arpsintrp"

        input_files = list(WRFRUN_NEW.resource.get_custom_resource(input_ref).iterdir())
        grid_base_file = next(file for file in input_files if re.fullmatch(r".+\.(?:hdf|h5f)grdbas", file.name))
        history_files = sorted(file for file in input_files if re.fullmatch(r".+\.(?:hdf|h5f)\d{6}", file.name))

        self.add_input_files([input_ref / file.name for file in [grid_base_file, *history_files]])
        WRFRUN_NEW.namelist.update_namelist(
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
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arpsintrp"
        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")
        self._stage_history_data()
        WRFRUN_NEW.namelist.update_namelist({"jobname": {"runname": self.name}, "output": {"dirname": "./outputs/"}}, "arpsintrp")
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arpsintrp")
        super().before_exec()

    def after_exec(self):
        """Archive generated boundary data and the runtime namelist."""
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
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
