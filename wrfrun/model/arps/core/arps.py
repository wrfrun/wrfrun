"""
wrfrun.model.arps.core.arps
###########################

ARPS forecast executable.

.. autosummary::
    :toctree: generated/

    ARPS
"""

import glob
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from wrfrun.core import WRFRUN, ExecutableBase, ResourceRef, ResultSource

from ..io import IORequirement, stage_io_requirements
from ._common import prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


class ARPSInputsRules:
    """ARPS input rules."""

    @classmethod
    def _stage_sfcdata(cls, executable: "ARPS", _: dict) -> None:
        source = WRFRUN.resource.get_result_ref("arpssfc", source=executable.arpssfc_source) / "arpssfc.sfcdata"
        executable.add_input_files(source)
        WRFRUN.namelist.update_namelist({"soil_ebm": {"sfcdtfl": "./arpssfc.sfcdata"}}, "arps")

    @classmethod
    def _stage_histories(cls, executable: "ARPS", namelist: dict) -> None:
        if executable.history_source is not None:
            input_ref = WRFRUN.resource.get_result_ref(source=executable.history_source)

        else:
            input_ref = WRFRUN.resource.INPUT_DIR / "arps"

        grid_base = Path(namelist.get("initialization", {}).get("inigbf")).name
        input_history = Path(namelist.get("initialization", {}).get("inifile")).name
        input_dir = WRFRUN.resource.get_custom_resource(input_ref)

        if not (input_dir / grid_base).is_file():
            message = f"Can't find your grid base file '{grid_base}' in {input_dir}."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        if not (input_dir / input_history).is_file():
            message = f"Can't find your history file '{input_history}' in {input_dir}."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        executable.add_input_files([input_ref / grid_base, input_ref / input_history])

        WRFRUN.namelist.update_namelist(
            {"initialization": {"inigbf": f"./{grid_base}", "inifile": f"./{input_history}"}},
            "arps",
        )

    @classmethod
    def _stage_sounding(cls, executable: "ARPS", namelist: dict) -> None:
        sounding_file = Path(namelist["initialization"]["sndfile"]).name
        executable.add_input_files(WRFRUN.resource.INPUT_DIR / sounding_file)

    @classmethod
    def _stage_arpsintrp_exbc(cls, executable: "ARPS", _: dict) -> None:
        source = WRFRUN.resource.get_result_ref("arpsintrp", source=executable.arpsintrp_source)
        filenames = sorted(glob.glob("arpsintrp.[0-9]*", root_dir=WRFRUN.resource.get_custom_resource(source)))
        if len(filenames) < 2:
            raise FileNotFoundError("Can't find enough arpsintrp EXBC outputs to run ARPS.")

        boundary_times = [datetime.strptime(name.removeprefix("arpsintrp."), "%Y%m%d.%H%M%S") for name in filenames]
        executable.add_input_files([source / name for name in filenames])
        WRFRUN.namelist.update_namelist(
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
        source = WRFRUN.resource.get_result_ref("arps") / restart_file

        # then check input dir
        if not WRFRUN.resource.get_custom_resource(source).is_file():
            source = WRFRUN.resource.INPUT_DIR / "arps" / restart_file

        if not WRFRUN.resource.get_custom_resource(source).is_file():
            message = f"Can't find your restart file '{restart_file}' both in input and output directory."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        executable.add_input_files(source)
        WRFRUN.namelist.update_namelist(
            {"initialization": {"rstinf": f"./{restart_file}"}},
            "arps",
        )


ARPS_INPUT_REQUIREMENTS = (
    IORequirement("sfcdata", lambda _, namelist: namelist["soil_ebm"]["sfcdat"] == 2, ARPSInputsRules._stage_sfcdata),
    IORequirement("history", lambda _, namelist: namelist["initialization"]["initopt"] == 3, ARPSInputsRules._stage_histories),
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


ARPS_OUTPUT_REUQIREMENTS = (
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
)


class ARPS(ExecutableBase):
    """Run the serial or MPI ARPS forecast executable."""

    def __init__(
        self,
        core_num: int | None = None,
        arpssfc_source: ResultSource | None = None,
        arpsintrp_source: ResultSource | None = None,
        history_source: ResultSource | None = None,
    ):
        """Create an ARPS executable and select its upstream result sources."""
        self.arpssfc_source = arpssfc_source
        self.arpsintrp_source = arpsintrp_source
        self.history_source = history_source

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
        """Store ARPS namelist and upstream result sources for replay."""
        self.custom_config.update(
            {
                "arpssfc_source": asdict(self.arpssfc_source) if self.arpssfc_source is not None else None,
                "arpsintrp_source": asdict(self.arpsintrp_source) if self.arpsintrp_source is not None else None,
                "history_source": asdict(self.history_source) if self.history_source is not None else None,
                "namelist": WRFRUN.namelist.get_namelist("arps"),
            }
        )

    def load_custom_config(self):
        """Restore ARPS namelist and upstream result sources for replay."""
        arpssfc_source = self.custom_config["arpssfc_source"]
        arpsintrp_source = self.custom_config["arpsintrp_source"]
        history_source = self.custom_config["history_source"]
        self.arpssfc_source = ResultSource(**arpssfc_source) if arpssfc_source is not None else None
        self.arpsintrp_source = ResultSource(**arpsintrp_source) if arpsintrp_source is not None else None
        self.history_source = ResultSource(**history_source) if history_source is not None else None
        WRFRUN.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        """Stage inputs and write the ARPS namelist."""
        WRFRUN.states.check_wrfrun_context(True)
        WRFRUN.states.WRFRUN_WORK_STATUS = "arps"
        WRFRUN.resource.mkdir(self.work_path / "outputs")
        namelist = WRFRUN.namelist.get_namelist("arps")

        stage_io_requirements(self, namelist, ARPS_INPUT_REQUIREMENTS)
        WRFRUN.namelist.update_namelist({"jobname": {"runname": self.name}}, "arps")
        WRFRUN.namelist.write_namelist(self.namelist_path, "arps")
        super().before_exec()

    def after_exec(self):
        """Archive ARPS outputs selected by the namelist."""
        namelist = WRFRUN.namelist.get_namelist("arps")

        if not WRFRUN.states.IS_IN_REPLAY:
            stage_io_requirements(self, namelist, ARPS_OUTPUT_REUQIREMENTS)

        super().after_exec()


__all__ = ["ARPS"]
