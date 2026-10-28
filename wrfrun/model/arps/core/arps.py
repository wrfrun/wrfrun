"""
ARPS forecast executable.

.. autosummary::
    :toctree: generated/

    ARPS
"""

import glob
import logging
from datetime import datetime
from pathlib import Path

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from ._common import prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


class ARPS(ExecutableBase):
    """Run the serial or MPI ARPS forecast executable."""

    def __init__(
        self,
        core_num: int | None = None,
        use_arpsintrp_exbc: bool = False,
        arpssfc_run_id: str | None = None,
        ext2arps_run_id: str | None = None,
        arpsintrp_run_id: str | None = None,
    ):
        """Create an ARPS executable and select its upstream result runs."""
        self.use_arpsintrp_exbc = use_arpsintrp_exbc
        self.arpssfc_run_id = arpssfc_run_id
        self.ext2arps_run_id = ext2arps_run_id
        self.arpsintrp_run_id = arpsintrp_run_id

        if core_num is None or core_num == 1:
            cmd = "./arps"
            work_path = ResourceRef("workspace_arps", "arps")
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = None
            LOGGER.info("Use serial arps.")
        else:
            cmd = "./arps_mpi"
            work_path = ResourceRef("workspace_arps", "arps_mpi")
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num
            LOGGER.info("Use parallel arps.")

        self.namelist_path = work_path / "arps.nml"
        super().__init__(
            name="arps",
            cmd=cmd,
            work_path=work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        prepare_arps_namelist("arps")

    def generate_custom_config(self):
        """Store ARPS namelist and upstream run choices for replay."""
        self.custom_config.update(
            {
                "arpssfc_run_id": self.arpssfc_run_id,
                "ext2arps_run_id": self.ext2arps_run_id,
                "arpsintrp_run_id": self.arpsintrp_run_id,
                "namelist": WRFRUN_NEW.namelist.get_namelist("arps"),
            }
        )

    def load_custom_config(self):
        """Restore ARPS namelist and upstream run choices for replay."""
        self.arpssfc_run_id = self.custom_config["arpssfc_run_id"]
        self.ext2arps_run_id = self.custom_config["ext2arps_run_id"]
        self.arpsintrp_run_id = self.custom_config["arpsintrp_run_id"]
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arps"
        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")
        model_config = WRFRUN_NEW.namelist.get_namelist("arps")

        if model_config["soil_ebm"]["sfcdat"] == 2:
            self.add_input_files(WRFRUN_NEW.resource.get_result_ref("arpssfc", self.arpssfc_run_id) / "arpssfc.sfcdata")
            WRFRUN_NEW.namelist.update_namelist({"soil_ebm": {"sfcdtfl": "./arpssfc.sfcdata"}}, "arps")

        if model_config["initialization"]["initopt"] == 3:
            ext2arps_ref = WRFRUN_NEW.resource.get_result_ref("ext2arps", self.ext2arps_run_id)
            ext2arps_files = glob.glob("ext2arps.*", root_dir=WRFRUN_NEW.resource.get_custom_resource(ext2arps_ref))
            if len(ext2arps_files) < 2:
                message = "Can't find all ext2arps outputs in outputs directory, which is essential to run arps."
                LOGGER.error(message)
                raise FileNotFoundError(message)

            self.add_input_files([ext2arps_ref / name for name in ext2arps_files])
            WRFRUN_NEW.namelist.update_namelist(
                {"initialization": {"inifile": "./ext2arps.hdf000000", "inigbf": "./ext2arps.hdfgrdbas"}}, "arps"
            )
        elif model_config["initialization"]["initopt"] == 1 and model_config["initialization"]["inibasopt"] == 1:
            sounding_file = Path(model_config["initialization"]["sndfile"]).name
            self.add_input_files(WRFRUN_NEW.resource.INPUT_DIR / sounding_file)

        if model_config["boundary_condition_options"]["lbcopt"] == 2 and self.use_arpsintrp_exbc:
            arpsintrp_ref = WRFRUN_NEW.resource.get_result_ref("arpsintrp", self.arpsintrp_run_id)
            arpsintrp_files = sorted(
                glob.glob("arpsintrp.[0-9]*", root_dir=WRFRUN_NEW.resource.get_custom_resource(arpsintrp_ref))
            )
            if len(arpsintrp_files) < 2:
                raise FileNotFoundError("Can't find enough arpsintrp EXBC outputs to run ARPS.")

            boundary_times = [datetime.strptime(name.removeprefix("arpsintrp."), "%Y%m%d.%H%M%S") for name in arpsintrp_files]
            self.add_input_files([arpsintrp_ref / name for name in arpsintrp_files])
            WRFRUN_NEW.namelist.update_namelist(
                {
                    "exbcpara": {
                        "exbcname": "./arpsintrp",
                        "tinitebd": boundary_times[0].strftime("%Y-%m-%d.%H:%M:%S"),
                        "tintvebd": int((boundary_times[1] - boundary_times[0]).total_seconds()),
                        "exbcfmt": 3,
                    }
                },
                "arps",
            )
        WRFRUN_NEW.namelist.update_namelist({"jobname": {"runname": self.name}}, "arps")
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arps")
        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.hdf",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
                no_file_error=False,
            )
            self.add_output_files(
                startswith=f"{self.name}.h5f",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
                no_file_error=False,
            )
            self.add_output_files(
                filenames="arps.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )
            self.add_output_files(
                filenames=f"{self.name}.sound",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path / "logs",
                no_file_error=False,
            )

        super().after_exec()


__all__ = ["ARPS"]
