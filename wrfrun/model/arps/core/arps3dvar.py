"""
ARPS three-dimensional variational analysis executable.

.. autosummary::
    :toctree: generated/

    ARPS3DVar
"""

import logging
from dataclasses import asdict
from os import listdir
from os.path import exists

from wrfrun.core import WRFRUN, ExecutableBase, ResourceRef, ResultSource

from ._common import prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


class ARPS3DVar(ExecutableBase):
    """Run ARPS 3DVAR using archived ARPS fields as background data."""

    def __init__(self, arps_source: ResultSource | None = None):
        """Create an ``arps3dvar`` executable."""
        work_path = ResourceRef("workspace_arps", "arps3dvar")
        self.namelist_path = work_path / "arps3dvar.nml"
        super().__init__(
            name="arps3dvar",
            cmd="./arps3dvar",
            work_path=work_path,
            stdin_file=self.namelist_path,
        )

        self.arps_source = arps_source
        prepare_arps_namelist("arps3dvar")

    def generate_custom_config(self):
        """Store the selected ARPS source and namelist for replay."""
        self.custom_config.update(
            {
                "arps_source": asdict(self.arps_source) if self.arps_source is not None else None,
                "namelist": WRFRUN.namelist.get_namelist("arps3dvar"),
            }
        )

    def load_custom_config(self):
        """Restore the selected ARPS source and namelist for replay."""
        arps_source = self.custom_config["arps_source"]
        self.arps_source = ResultSource(**arps_source) if arps_source is not None else None
        WRFRUN.namelist.update_namelist(self.custom_config["namelist"], "arps3dvar")

    def before_exec(self):
        """Stage ARPS background data and write the 3DVAR namelist."""
        background_files = ["arps.hdf000000", "arps.hdfgrdbas"]
        WRFRUN.states.check_wrfrun_context(True)
        WRFRUN.states.WRFRUN_WORK_STATUS = "arps3dvar"
        WRFRUN.resource.mkdir(self.work_path / "outputs")

        work_dir = WRFRUN.resource.get_custom_resource(self.work_path)
        missing_files = [name for name in background_files if name not in listdir(work_dir)]
        if missing_files:
            arps_ref = WRFRUN.resource.get_result_ref("arps", source=self.arps_source)
            arps_dir = WRFRUN.resource.get_custom_resource(arps_ref)
            missing_sources = [name for name in missing_files if not exists(f"{arps_dir}/{name}")]
            if missing_sources:
                message = (
                    "Can't find required ARPS background files in the arps3dvar work directory or "
                    f"'{arps_dir}': {', '.join(missing_sources)}"
                )
                LOGGER.error(message)
                raise FileNotFoundError(message)
            self.add_input_files([arps_ref / name for name in missing_files])

        updates = {
            "jobname": {"runname": self.name},
            "initialization": {"inifile": "./arps.hdf000000", "inigbf": "./arps.hdfgrdbas"},
            "output": {"dirname": "./outputs/"},
        }
        if WRFRUN.namelist.get_namelist("arps3dvar")["incr_out"]["incrdmp"] > 0:
            updates["incr_out"] = {"incdmpf": f"./outputs/{self.name}.incr"}

        WRFRUN.namelist.update_namelist(updates, "arps3dvar")
        WRFRUN.namelist.write_namelist(self.namelist_path, "arps3dvar")
        super().before_exec()

    def after_exec(self):
        """Archive 3DVAR outputs and its runtime namelist."""
        if not WRFRUN.states.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )
            self.add_output_files(
                filenames=[f"{self.name}.lst", f"{self.name}.adasstat", f"{self.name}.adasstn", "arps3dvar.nml"],
                output_dir=self.work_path,
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()


__all__ = ["ARPS3DVar"]
