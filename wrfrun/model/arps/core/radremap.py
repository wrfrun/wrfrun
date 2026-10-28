"""
ARPS radar-remapping executable.

.. autosummary::
    :toctree: generated/

    RadRemap
"""

from datetime import timedelta
from pathlib import Path

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from ._common import prepare_component_namelist


class RadRemap(ExecutableBase):
    """Remap a radar volume with an archived ARPS background state."""

    def __init__(self, arps_run_id: str | None = None):
        """Create a serial ``radremap`` executable."""
        work_path = ResourceRef("workspace_arps", "radremap")
        self.namelist_path = work_path / "radremap.nml"
        super().__init__(
            name="radremap",
            cmd="./radremap",
            work_path=work_path,
            stdin_file=self.namelist_path,
        )

        self.arps_run_id = arps_run_id
        prepare_component_namelist("radremap")

    def generate_custom_config(self):
        """Store the selected ARPS run and ``radremap`` namelist for replay."""
        self.custom_config.update({"arps_run_id": self.arps_run_id, "namelist": WRFRUN_NEW.namelist.get_namelist("radremap")})

    def load_custom_config(self):
        """Restore the selected ARPS run and ``radremap`` namelist for replay."""
        if not WRFRUN_NEW.namelist.check_namelist_id("radremap"):
            WRFRUN_NEW.namelist.register_namelist_id("radremap")
        self.arps_run_id = self.custom_config["arps_run_id"]
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "radremap")

    def before_exec(self):
        """Stage input data and write the runtime ``radremap`` namelist."""
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "radremap"
        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        namelist = WRFRUN_NEW.namelist.get_namelist("radremap")
        history_file = Path(namelist["initialization"]["inifile"]).name
        grid_base_file = Path(namelist["initialization"]["inigbf"]).name
        radar_file = Path(namelist["radremapopt"]["radfname"]).name
        outtime = int(history_file[-6:])
        valid_time = WRFRUN_NEW.config["simulation"]["time"]["start_time"] + timedelta(seconds=outtime)

        arps_ref = WRFRUN_NEW.resource.get_result_ref("arps", self.arps_run_id)
        self.add_input_files([arps_ref / history_file, arps_ref / grid_base_file])
        self.add_input_files(WRFRUN_NEW.resource.INPUT_DIR / "radremap" / radar_file, is_output=False)
        WRFRUN_NEW.namelist.update_namelist(
            {
                "message_passing": {"nproc_x": 1, "nproc_y": 1, "nprocx_in": 1, "nprocy_in": 1},
                "initialization": {
                    "modelopt": 1,
                    "initime": valid_time.strftime("%Y-%m-%d_%H:%M:%S"),
                    "initopt": 3,
                    "inifmt": 3,
                    "inisplited": 0,
                    "inifile": f"./{history_file}",
                    "inigbf": f"./{grid_base_file}",
                },
                "radremapopt": {"radfname": f"./{radar_file}"},
                "radremapout": {"dirname": "./outputs/", "outtime": outtime},
            },
            "radremap",
        )
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "radremap")
        super().before_exec()

    def after_exec(self):
        """Archive remapped radar products and the runtime namelist."""
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            self.add_output_files(
                startswith="",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )
            self.add_output_files(
                filenames="radremap.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


__all__ = ["RadRemap"]
