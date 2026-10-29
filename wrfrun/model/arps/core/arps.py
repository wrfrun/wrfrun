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

from ..io import IORequirement, stage_io_requirements
from ._common import prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


class ARPSInputsRules:
    """ARPS input rules."""

    @classmethod
    def _stage_sfcdata(cls, executable: "ARPS", _: dict) -> None:
        source = WRFRUN_NEW.resource.get_result_ref("arpssfc", executable.arpssfc_run_id) / "arpssfc.sfcdata"
        executable.add_input_files(source)
        WRFRUN_NEW.namelist.update_namelist({"soil_ebm": {"sfcdtfl": "./arpssfc.sfcdata"}}, "arps")

    @classmethod
    def _stage_ext2arps(cls, executable: "ARPS", _: dict) -> None:
        source = WRFRUN_NEW.resource.get_result_ref("ext2arps", executable.ext2arps_run_id)
        filenames = glob.glob("ext2arps.*", root_dir=WRFRUN_NEW.resource.get_custom_resource(source))
        if len(filenames) < 2:
            message = "Can't find all ext2arps outputs in outputs directory, which is essential to run arps."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        executable.add_input_files([source / name for name in filenames])
        WRFRUN_NEW.namelist.update_namelist(
            {"initialization": {"inifile": "./ext2arps.hdf000000", "inigbf": "./ext2arps.hdfgrdbas"}}, "arps"
        )

    @classmethod
    def _stage_sounding(cls, executable: "ARPS", namelist: dict) -> None:
        sounding_file = Path(namelist["initialization"]["sndfile"]).name
        executable.add_input_files(WRFRUN_NEW.resource.INPUT_DIR / sounding_file)

    @classmethod
    def _stage_arpsintrp_exbc(cls, executable: "ARPS", _: dict) -> None:
        source = WRFRUN_NEW.resource.get_result_ref("arpsintrp", executable.arpsintrp_run_id)
        filenames = sorted(glob.glob("arpsintrp.[0-9]*", root_dir=WRFRUN_NEW.resource.get_custom_resource(source)))
        if len(filenames) < 2:
            raise FileNotFoundError("Can't find enough arpsintrp EXBC outputs to run ARPS.")

        boundary_times = [datetime.strptime(name.removeprefix("arpsintrp."), "%Y%m%d.%H%M%S") for name in filenames]
        executable.add_input_files([source / name for name in filenames])
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

    @classmethod
    def _stage_restart_data(cls, executable: "ARPS", namelist: dict):
        restart_file = Path(namelist.get("initialization", {}).get("rstinf")).name

        # check public results first
        source = WRFRUN_NEW.resource.get_result_ref("arps") / restart_file

        # then check input dir
        if not WRFRUN_NEW.resource.get_custom_resource(source).is_file():
            source = WRFRUN_NEW.resource.INPUT_DIR / "arps" / restart_file

        if not WRFRUN_NEW.resource.get_custom_resource(source).is_file():
            message = f"Can't find your restart file '{restart_file}' both in input and output directory."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        executable.add_input_files(source)
        WRFRUN_NEW.namelist.update_namelist(
            {"initialization": {"rstinf": f"./{restart_file}"}},
            "arps",
        )


ARPS_INPUT_REQUIREMENTS = (
    IORequirement("sfcdata", lambda _, namelist: namelist["soil_ebm"]["sfcdat"] == 2, ARPSInputsRules._stage_sfcdata),
    IORequirement("ext2arps", lambda _, namelist: namelist["initialization"]["initopt"] == 3, ARPSInputsRules._stage_ext2arps),
    IORequirement(
        "sounding",
        lambda _, namelist: namelist["initialization"]["initopt"] == 1 and namelist["initialization"]["inibasopt"] == 1,
        ARPSInputsRules._stage_sounding,
    ),
    IORequirement(
        "arpsintrp_exbc",
        lambda executable, namelist: (
            executable.use_arpsintrp_exbc  # type: ignore
            and namelist["boundary_condition_options"]["lbcopt"] == 2
        ),
        ARPSInputsRules._stage_arpsintrp_exbc,
    ),
    IORequirement(
        "restart",
        lambda _, namelist: namelist["initialization"]["initopt"] == 2,
        ARPSInputsRules._stage_restart_data,
    ),
)


class ARPSOutputsRules:
    """ARPS output rules."""

    @classmethod
    def _stage_essential_outputs(cls, executable: "ARPS", namelist: dict):
        executable.add_output_files(
            startswith=f"{executable.name}.hdf",
            output_dir=executable.work_path / "outputs",
            save_path=executable.OUTPUT_SAVE_PATH,
            no_file_error=False,
        )
        executable.add_output_files(
            startswith=f"{executable.name}.h5f",
            output_dir=executable.work_path / "outputs",
            save_path=executable.OUTPUT_SAVE_PATH,
            no_file_error=False,
        )
        executable.add_output_files(
            filenames="arps.nml",
            output_dir=executable.work_path,
            save_path=executable.LOG_SAVE_PATH,
        )
        executable.add_output_files(
            filenames=f"{executable.name}.sound",
            output_dir=executable.work_path / "outputs",
            save_path=executable.LOG_SAVE_PATH,
            no_file_error=False,
        )

    @classmethod
    def _stage_output_restart_datas(cls, executable: "ARPS", namelist: dict):
        executable.add_output_files(
            startswith=f"{executable.name}.rst",
            output_dir=executable.work_path / "outputs",
            save_path=executable.OUTPUT_SAVE_PATH,
        )


ARPS_OUTPUT_REUQIREMENTS = {
    IORequirement(
        "results",
        lambda i, j: True,
        ARPSOutputsRules._stage_essential_outputs,
    ),
    IORequirement(
        "restart",
        lambda _, namelist: namelist.get("output", {}).get("trstout", 0.0) > 0.0,
        ARPSOutputsRules._stage_output_restart_datas,
    ),
}


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
        namelist = WRFRUN_NEW.namelist.get_namelist("arps")

        stage_io_requirements(self, namelist, ARPS_INPUT_REQUIREMENTS)
        WRFRUN_NEW.namelist.update_namelist({"jobname": {"runname": self.name}}, "arps")
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arps")
        super().before_exec()

    def after_exec(self):
        namelist = WRFRUN_NEW.namelist.get_namelist("arps")

        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            stage_io_requirements(self, namelist, ARPS_OUTPUT_REUQIREMENTS)

        super().after_exec()


__all__ = ["ARPS"]
