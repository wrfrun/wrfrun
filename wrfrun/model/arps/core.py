"""
wrfrun.model.arps.core
######################

Core implementation of ARPS model.

If you prefer function interfaces, please see :doc:`function wrapper </api/model.arps.exec_wrap>` for these ``Executable``.

.. autosummary::
    :toctree: generated/

    ARPSSFC
    ARPS
    ARPS3DVar
    EXT2ARPS
"""

import glob
import logging
from datetime import datetime, timedelta
from os import listdir
from os.path import exists
from typing import Optional

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from .namelist import prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


def _check_and_prepare_namelist():
    if not WRFRUN_NEW.namelist.check_namelist("arps"):
        prepare_arps_namelist()


class ARPSSFC(ExecutableBase):
    """
    ``Executable`` for "arpssfc".

    .. py:attribute:: work_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of arpssfc workspace path.

    .. py:attribute:: namelist_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of arpssfc namelist path.
    """

    def __init__(self):
        """
        ``Executable`` for "arpssfc".
        """
        mpi_use = False
        mpi_cmd = None
        mpi_core_num = None

        work_path = ResourceRef("workspace_arps", "arpssfc")
        self.namelist_path = work_path / "arpssfc.nml"

        super().__init__(
            name="arpssfc",
            cmd="./arpssfc",
            work_path=work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("arps")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arpssfc"

        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        WRFRUN_NEW.namelist.update_namelist({"jobname": {"runname": self.name}}, "arps")
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            self.add_output_files(
                filenames=f"{self.name}.sfcdata",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )

            self.add_output_files(
                filenames="arpssfc.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


def _check_ext2arps_input_data() -> list[str]:
    """
    Check if the name of input data is consistent with the settings in namelist.

    Setting ``extdname``, ``nextdfil`` and ``extdtime`` in namelist will change
    the name and number of expected input data.

    **Example**

    If you have namelist settings like:

    .. code-block :: text
        &extdfile
            extdname = 'input',
            nextdfil = 7,  ! MARK: To be changed.
            extdtime(1) = '2025-12-01.00:00:00+000:00:00',
            extdtime(2) = '2025-12-01.00:00:00+001:00:00',
            extdtime(3) = '2025-12-01.00:00:00+002:00:00',
            extdtime(4) = '2025-12-01.00:00:00+003:00:00',
            extdtime(5) = '2025-12-01.00:00:00+004:00:00',
            extdtime(6) = '2025-12-01.00:00:00+005:00:00',
            extdtime(7) = '2025-12-01.00:00:00+006:00:00',
        /

    ``ext2arps`` will try to read seven input files:

    * input.2025120100f00
    * input.2025120100f01
    * input.2025120100f02
    * input.2025120100f03
    * input.2025120100f04
    * input.2025120100f05
    * input.2025120100f06

    :raise FillNotFoundError: If any expected input file isn't found.
    :return: Expected filename list.
    :rtype: list[str]
    """
    data_input_dir = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.INPUT_DIR / "ext2arps")
    namelist = WRFRUN_NEW.namelist.get_namelist("arps")
    extdname = namelist["extdfile"]["extdname"]
    nextdfil = namelist["extdfile"]["nextdfil"]
    extdtime = namelist["extdfile"]["extdtime"]

    if isinstance(extdtime, str):
        extdtime = [extdtime]

    if len(extdtime) < nextdfil:
        LOGGER.error(f"Expected {nextdfil} values in 'extdtime', but only got {len(extdtime)}.")
        raise ValueError(f"Expected {nextdfil} values in 'extdtime', but only got {len(extdtime)}.")

    expected_file_list: list[str] = []
    missing_file_list: list[str] = []

    for time_string in extdtime[:nextdfil]:
        try:
            init_time_string, forecast_time_string = time_string.split("+", maxsplit=1)
            init_time = datetime.strptime(init_time_string, "%Y-%m-%d.%H:%M:%S")
        except ValueError as exc:
            LOGGER.error(f"Invalid extdtime setting: '{time_string}'")
            raise ValueError(f"Invalid extdtime setting: '{time_string}'") from exc

        try:
            hour_str, minute_str, second_str = forecast_time_string.split(":")
            forecast_time = timedelta(
                hours=int(hour_str),
                minutes=int(minute_str),
                seconds=int(second_str),
            )
        except ValueError as exc:
            LOGGER.error(f"Invalid forecast offset in extdtime: '{time_string}'")
            raise ValueError(f"Invalid forecast offset in extdtime: '{time_string}'") from exc

        forecast_hour = int(forecast_time.total_seconds() // 3600)
        expected_file_name = f"{extdname}.{init_time.strftime('%Y%m%d%H')}f{forecast_hour:02d}"
        expected_file_list.append(expected_file_name)

        if not exists(f"{data_input_dir}/{expected_file_name}"):
            missing_file_list.append(expected_file_name)

    if len(missing_file_list) > 0:
        LOGGER.error(
            "Can't find required ext2arps input files in '%s': %s",
            data_input_dir,
            ", ".join(missing_file_list),
        )
        raise FileNotFoundError(f"Can't find required ext2arps input files in '{data_input_dir}': {', '.join(missing_file_list)}")

    return expected_file_list


class EXT2ARPS(ExecutableBase):
    """
    ``Executable`` for "ext2arps".

    .. py:attribute:: work_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of ext2arps workspace path.

    .. py:attribute:: namelist_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of ext2arps namelist path.
    """

    def __init__(self):
        """
        ``Executable`` for "ext2arps".
        """
        mpi_use = False
        mpi_cmd = None
        mpi_core_num = None

        work_path = ResourceRef("workspace_arps", "ext2arps")
        self.namelist_path = work_path / "ext2arps.nml"

        super().__init__(
            name="ext2arps",
            cmd="./ext2arps",
            work_path=work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("arps")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "ext2arps"

        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        input_file_list = _check_ext2arps_input_data()
        self.add_input_files([WRFRUN_NEW.resource.INPUT_DIR / "ext2arps" / file_name for file_name in input_file_list])

        _arpstrn_data_dir = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.OUTPUT_DIR / "arpstrn")
        _arpstrn_data = glob.glob("arpstrn.trndata*", root_dir=_arpstrn_data_dir)
        if len(_arpstrn_data) < 1:
            message = "Can't find arpstrn outputs in ext2arps outputs directory, which is essential to run ext2arps."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        _arpstrn_data_path = WRFRUN_NEW.resource.OUTPUT_DIR / "arpstrn" / _arpstrn_data[0]

        self.add_input_files(_arpstrn_data_path)

        WRFRUN_NEW.namelist.update_namelist(
            {
                "jobname": {"runname": self.name},
                "terrain": {"terndta": f"./{_arpstrn_data_path.name}"},
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
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()


class ARPS(ExecutableBase):
    """
    ``Executable`` for "arps".

    .. py:attribute:: work_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of arps workspace path.

    .. py:attribute:: namelist_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of arps namelist path.
    """

    def __init__(self, core_num: Optional[int] = None):
        """
        ``Executable`` for "arps".
        """
        if core_num is None or core_num == 1:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = None
            cmd = "./arps"
            work_path = ResourceRef("workspace_arps", "arps")

            LOGGER.info("Use serial arps.")

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num
            cmd = "./arps_mpi"
            work_path = ResourceRef("workspace_arps", "arps_mpi")

            LOGGER.info("Use parallel arps.")

        self.namelist_path = work_path / "arps.nml"

        super().__init__(
            name="arps",
            cmd=cmd,
            work_path=self.work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("arps")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arps"
        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        self.add_input_files(WRFRUN_NEW.resource.OUTPUT_DIR / "arpssfc/arpssfc.sfcdata")

        # find ext2arps outputs
        _ext2arps_out_dir_ref = WRFRUN_NEW.resource.OUTPUT_DIR / "ext2arps"
        _ext2arps_out_files = glob.glob("ext2arps.", root_dir=WRFRUN_NEW.resource.get_custom_resource(_ext2arps_out_dir_ref))

        if len(_ext2arps_out_files) < 2:
            message = "Can't find all ext2arps outputs in outputs directory, which is essential to run arps."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        self.add_input_files([_ext2arps_out_dir_ref / _file for _file in _ext2arps_out_files])

        WRFRUN_NEW.namelist.update_namelist(
            {
                "jobname": {"runname": self.name},
                "initialization": {"inifile": "./ext2arps.hdf000000", "inigbf": "./ext2arps.hdfgrdbas"},
                "soil_ebm": {"sfcdtfl": "./arpssfc.sfcdata"},
                "exbcpara": {"exbcname": "./ext2arps"},
            },
            "arps",
        )
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            arps_namelist = WRFRUN_NEW.namelist.get_namelist("arps")

            # try to calculate output file names based on history dump settings
            history_dump_option = arps_namelist["history_dump"]["hdmpopt"]
            if history_dump_option != 1:
                LOGGER.warning(f"History dump option {history_dump_option} isn't supported yet.")
                LOGGER.warning(
                    f"Save outputs manually in '{WRFRUN_NEW.resource.get_custom_resource(self.work_path / 'outputs')}'."
                )

            else:
                dump_time_step = arps_namelist["history_dump"]["thisdmp"]
                dump_time_start = arps_namelist["history_dump"]["tstrtdmp"]
                simulation_start_time = arps_namelist["timestep"]["tstart"]
                simulate_time = arps_namelist["timestep"]["tstop"]

                files_num = int(simulate_time // dump_time_step)
                dump_time_point = [int(i * dump_time_step) for i in range(files_num)]
                real_dump_start_time = dump_time_start if dump_time_start > simulation_start_time else simulation_start_time
                dump_time_point = [x for x in dump_time_point if x > real_dump_start_time]

                file_list = [f"{self.name}.hdf{str(x).rjust(6, '0')}" for x in dump_time_point]

                self.add_output_files(
                    filenames=file_list,
                    output_dir=self.work_path / "outputs",
                    save_path=self._output_save_path,
                )

            self.add_output_files(
                filenames=f"{self.name}.hdfgrdbas",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )

            # ARPS3DVAR uses the initial ARPS history file as its background.
            # The calculated periodic dump list above intentionally excludes
            # tstart, so preserve this file separately when ARPS produced it.
            self.add_output_files(
                filenames=f"{self.name}.hdf000000",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
                no_file_error=False,
            )

            self.add_output_files(
                filenames="arps.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


class ARPS3DVar(ExecutableBase):
    """
    ``Executable`` for ``arps3dvar``.

    The program uses an ARPS history file and its matching grid/base-state
    file as the background. Observation files and error-statistics tables are
    configured by the ADAS and 3DVAR sections of the ARPS namelist.

    :param arps_data_path: Directory containing the ARPS background files
                           ``arps.hdf000000`` and ``arps.hdfgrdbas``.  If it
                           is ``None``, use the archived ``arps`` output
                           directory.
    :type arps_data_path: str | None
    """

    def __init__(self):
        """
        ``Executable`` for ``arps3dvar``.

        :param arps_data_path: Directory containing the ARPS background
                               history and grid/base-state files.  If it is
                               ``None``, try the configured ARPS output path.
        :type arps_data_path: str | None
        """
        work_path = ResourceRef("workspace_arps", "arps3dvar")
        self.namelist_path = work_path / "arps3dvar.nml"

        super().__init__(
            name="arps3dvar",
            cmd="./arps3dvar",
            work_path=work_path,
            stdin_file=self.namelist_path,
        )

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """Store the ARPS namelist and selected background directory."""
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("arps")})

    def load_custom_config(self):
        """Restore the ARPS namelist and selected background directory."""
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        background_files = ["arps.hdf000000", "arps.hdfgrdbas"]

        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arps3dvar"
        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        work_dir = WRFRUN_NEW.resource.get_custom_resource(self.work_path)
        existing_files = listdir(work_dir)
        missing_background_files = [file_name for file_name in background_files if file_name not in existing_files]

        if missing_background_files:
            arps_data_path_ref = WRFRUN_NEW.resource.OUTPUT_DIR / "arps"
            arps_data_path = WRFRUN_NEW.resource.get_custom_resource(arps_data_path_ref)
            missing_source_files = [
                file_name for file_name in missing_background_files if not exists(f"{arps_data_path}/{file_name}")
            ]

            if missing_source_files:
                message = (
                    "Can't find required ARPS background files in the arps3dvar work directory or "
                    f"'{arps_data_path}': {', '.join(missing_source_files)}"
                )
                LOGGER.error(message)
                raise FileNotFoundError(message)

            self.add_input_files([arps_data_path_ref / file_name for file_name in missing_background_files])

        namelist_updates = {
            "jobname": {"runname": self.name},
            "initialization": {
                "inifile": "./arps.hdf000000",
                "inigbf": "./arps.hdfgrdbas",
            },
            "output": {"dirname": "./outputs/"},
        }
        if WRFRUN_NEW.namelist.get_namelist("arps")["incr_out"]["incrdmp"] > 0:
            namelist_updates["incr_out"] = {"incdmpf": f"./outputs/{self.name}.incr"}

        WRFRUN_NEW.namelist.update_namelist(namelist_updates, "arps")
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
                filenames=[f"{self.name}.lst", f"{self.name}.adasstat", f"{self.name}.adasstn", "arps3dvar.nml"],
                output_dir=self.work_path,
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()


__all__ = ["ARPSSFC", "ARPS", "ARPS3DVar", "EXT2ARPS"]
