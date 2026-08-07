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

import logging
from datetime import datetime, timedelta
from os import listdir
from os.path import exists
from typing import Optional

from wrfrun.core import WRFRUN, ExecutableBase, ExecutableDB
from wrfrun.workspace.arps import get_arps_workspace_path

from .namelist import prepare_arps_namelist

LOGGER = logging.getLogger("wrfrun")


def _check_and_prepare_namelist():
    wrfrun_config = WRFRUN.config

    if not wrfrun_config.check_namelist("arps"):
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

        self.work_path = f"{get_arps_workspace_path()}/arpssfc"
        self.namelist_path = f"{self.work_path}/arpssfc.nml"

        super().__init__(
            name="arpssfc",
            cmd="./arpssfc",
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
        self.custom_config.update({"namelist": WRFRUN.config.get_namelist("arps")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN.config.update_namelist(self.custom_config["namelist"], "arps")

    def before_exec(self):
        wrfrun_config = WRFRUN.config

        wrfrun_config.check_wrfrun_context(True)
        wrfrun_config.WRFRUN_WORK_STATUS = "arpssfc"

        WRFRUN.check_path(f"{self.work_path}/outputs")

        wrfrun_config.update_namelist({"jobname": {"runname": self.name}}, "arps")
        wrfrun_config.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        wrfrun_config = WRFRUN.config
        if not wrfrun_config.IS_IN_REPLAY:
            self.add_output_files(
                filenames=f"{self.name}.sfcdata",
                output_dir=f"{self.work_path}/outputs",
                save_path=self._output_save_path,
            )

            self.add_output_files(
                filenames="arpssfc.nml",
                output_dir=self.work_path,
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()

        LOGGER.info(f"All arpssfc output files have been copied to {WRFRUN.uri.parse_resource_uri(self._output_save_path)}")


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
    data_input_dir = WRFRUN.config.get_input_data_path("ext2arps")
    namelist = WRFRUN.config.get_namelist("arps")
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

    def __init__(self, arpstrn_data_path: Optional[str] = None):
        """
        ``Executable`` for "ext2arps".

        :param arpstrn_data_path: Directory path of :class:`ARPSTRN <wrfrun.model.arps.arpstrn.ARPSTRN>` outputs.
                                  If is ``None``, try to use the output path specified by config file.
        :type arpstrn_data_path: str
        """
        mpi_use = False
        mpi_cmd = None
        mpi_core_num = None

        self.work_path = f"{get_arps_workspace_path()}/ext2arps"
        self.namelist_path = f"{self.work_path}/ext2arps.nml"
        self.arpstrn_data_path = arpstrn_data_path

        super().__init__(
            name="ext2arps",
            cmd="./ext2arps",
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
        self.custom_config.update(
            {
                "namelist": WRFRUN.config.get_namelist("arps"),
                "arpstrn_data_path": self.arpstrn_data_path,
            }
        )

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN.config.update_namelist(self.custom_config["namelist"], "arps")
        self.arpstrn_data_path = self.custom_config["arpstrn_data_path"]

    def before_exec(self):
        wrfrun_config = WRFRUN.config

        wrfrun_config.check_wrfrun_context(True)
        wrfrun_config.WRFRUN_WORK_STATUS = "ext2arps"

        WRFRUN.check_path(f"{self.work_path}/outputs")

        input_file_list = _check_ext2arps_input_data()
        self.add_input_files([f"{wrfrun_config.get_input_data_path('ext2arps')}/{file_name}" for file_name in input_file_list])

        # check existed arpstrn outputs
        file_list = listdir(WRFRUN.uri.parse_resource_uri(self.work_path))

        if "arpstrn.trndata" not in file_list:
            if self.arpstrn_data_path is None:
                self.arpstrn_data_path = f"{WRFRUN.uri.WRFRUN_OUTPUT_PATH}/arpstrn/arpstrn.trndata"
            arpstrn_data_path = WRFRUN.uri.parse_resource_uri(self.arpstrn_data_path)

            if not exists(arpstrn_data_path):
                LOGGER.error(
                    "Can't find arpstrn outputs both in ext2arps work dir and your outputs directory, "
                    "which is essential to run ext2arps."
                )
                raise FileNotFoundError(
                    "Can't find arpstrn outputs both in ext2arps work dir and your outputs directory, "
                    "which is essential to run ext2arps."
                )

            else:
                self.add_input_files(self.arpstrn_data_path)

        wrfrun_config.update_namelist(
            {
                "jobname": {"runname": self.name},
                "terrain": {"terndta": "./arpstrn.trndata"},
                "extdfile": {"dir_extd": "./", "grdbasopt": 1},
            },
            "arps",
        )
        wrfrun_config.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        wrfrun_config = WRFRUN.config
        if not wrfrun_config.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.",
                output_dir=f"{self.work_path}/outputs",
                save_path=self._output_save_path,
            )

            self.add_output_files(
                filenames="ext2arps.nml",
                output_dir=self.work_path,
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()

        LOGGER.info(f"All ext2arps output files have been copied to {WRFRUN.uri.parse_resource_uri(self._output_save_path)}")


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

    def __init__(
        self, arpssfc_data_path: Optional[str] = None, ext2arps_data_path: Optional[str] = None, core_num: Optional[int] = None
    ):
        """
        ``Executable`` for "arps".

        :param arpssfc_data_path: Directory path of :class:`ARPSSFC` outputs.
                                  If is ``None``, try to use the output path specified by config file.
        :type arpssfc_data_path: str
        :param ext2arps_data_path: Directory path of :class:`EXT2ARPS` outputs.
                                  If is ``None``, try to use the output path specified by config file.
        :type ext2arps_data_path: str
        """
        if core_num is None or core_num == 1:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = None
            cmd = "./arps"
            self.work_path = f"{get_arps_workspace_path()}/arps"

            LOGGER.info("Use serial arps.")

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num
            cmd = "./arps_mpi"
            self.work_path = f"{get_arps_workspace_path()}/arps_mpi"

            LOGGER.info("Use parallel arps.")

        self.namelist_path = f"{self.work_path}/arps.nml"
        self.arpssfc_data_path = arpssfc_data_path
        self.ext2arps_data_path = ext2arps_data_path

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
        self.custom_config.update(
            {
                "namelist": WRFRUN.config.get_namelist("arps"),
                "arpssfc_data_path": self.arpssfc_data_path,
                "ext2arps_data_path": self.ext2arps_data_path,
            }
        )

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN.config.update_namelist(self.custom_config["namelist"], "arps")
        self.arpssfc_data_path = self.custom_config["arpssfc_data_path"]
        self.ext2arps_data_path = self.custom_config["ext2arps_data_path"]

    def before_exec(self):
        wrfrun_config = WRFRUN.config

        wrfrun_config.check_wrfrun_context(True)
        wrfrun_config.WRFRUN_WORK_STATUS = "arps"

        WRFRUN.check_path(f"{self.work_path}/outputs")

        # check existed arpssfc outputs
        file_list = listdir(WRFRUN.uri.parse_resource_uri(self.work_path))

        if "arpssfc.sfcdata" not in file_list:
            if self.arpssfc_data_path is None:
                self.arpssfc_data_path = f"{WRFRUN.uri.WRFRUN_OUTPUT_PATH}/arpssfc/arpssfc.sfcdata"
            arpssfc_data_path = WRFRUN.uri.parse_resource_uri(self.arpssfc_data_path)

            if not exists(arpssfc_data_path):
                LOGGER.error(
                    "Can't find arpssfc outputs both in arps work dir and your outputs directory, which is essential to run arps."
                )
                raise FileNotFoundError(
                    "Can't find arpssfc outputs both in arps work dir and your outputs directory, which is essential to run arps."
                )

            else:
                self.add_input_files(self.arpssfc_data_path)

        # check existed ext2arps outputs
        if "ext2arps.hdfgrdbas" not in file_list:
            if self.ext2arps_data_path is None:
                self.ext2arps_data_path = f"{WRFRUN.uri.WRFRUN_OUTPUT_PATH}/ext2arps"
            ext2arps_data_path = WRFRUN.uri.parse_resource_uri(self.ext2arps_data_path)

            if not exists(f"{ext2arps_data_path}/ext2arps.hdfgrdbas"):
                LOGGER.error(
                    "Can't find ext2arps outputs both in arps work dir and your outputs directory, which is essential to run arps."
                )
                raise FileNotFoundError(
                    "Can't find ext2arps outputs both in arps work dir and your outputs directory, which is essential to run arps."
                )

            else:
                ext2arps_outputs = listdir(ext2arps_data_path)
                self.add_input_files([f"{self.ext2arps_data_path}/{_file}" for _file in ext2arps_outputs])

        wrfrun_config.update_namelist(
            {
                "jobname": {"runname": self.name},
                "initialization": {"inifile": "./ext2arps.hdf000000", "inigbf": "./ext2arps.hdfgrdbas"},
                "soil_ebm": {"sfcdtfl": "./arpssfc.sfcdata"},
                "exbcpara": {"exbcname": "./ext2arps"},
            },
            "arps",
        )
        wrfrun_config.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        wrfrun_config = WRFRUN.config

        if not wrfrun_config.IS_IN_REPLAY:
            arps_namelist = wrfrun_config.get_namelist("arps")

            # try to calculate output file names based on history dump settings
            history_dump_option = arps_namelist["history_dump"]["hdmpopt"]
            if history_dump_option != 1:
                LOGGER.warning(f"History dump option {history_dump_option} isn't supported yet.")
                LOGGER.warning(
                    f"You have to save ARPS results manually in '{WRFRUN.uri.parse_resource_uri(self.work_path)}/outputs'."
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
                    output_dir=f"{self.work_path}/outputs",
                    save_path=self._output_save_path,
                )

            self.add_output_files(
                filenames=f"{self.name}.hdfgrdbas",
                output_dir=f"{self.work_path}/outputs",
                save_path=self._output_save_path,
            )

            # ARPS3DVAR uses the initial ARPS history file as its background.
            # The calculated periodic dump list above intentionally excludes
            # tstart, so preserve this file separately when ARPS produced it.
            self.add_output_files(
                filenames=f"{self.name}.hdf000000",
                output_dir=f"{self.work_path}/outputs",
                save_path=self._output_save_path,
                no_file_error=False,
            )

            self.add_output_files(
                filenames="arps.nml",
                output_dir=self.work_path,
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()

        LOGGER.info(f"All arps output files have been copied to {WRFRUN.uri.parse_resource_uri(self._output_save_path)}")


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

    def __init__(self, arps_data_path: Optional[str] = None):
        """
        ``Executable`` for ``arps3dvar``.

        :param arps_data_path: Directory containing the ARPS background
                               history and grid/base-state files.  If it is
                               ``None``, try the configured ARPS output path.
        :type arps_data_path: str | None
        """
        self.work_path = f"{get_arps_workspace_path()}/arps3dvar"
        self.namelist_path = f"{self.work_path}/arps3dvar.nml"
        self.arps_data_path = arps_data_path

        super().__init__(
            name="arps3dvar",
            cmd="./arps3dvar",
            work_path=self.work_path,
            stdin_file=self.namelist_path,
        )

        self.class_config["class_kwargs"] = {"arps_data_path": arps_data_path}
        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """Store the ARPS namelist and selected background directory."""
        self.custom_config.update(
            {
                "namelist": WRFRUN.config.get_namelist("arps"),
                "arps_data_path": self.arps_data_path,
            }
        )

    def load_custom_config(self):
        """Restore the ARPS namelist and selected background directory."""
        WRFRUN.config.update_namelist(self.custom_config["namelist"], "arps")
        self.arps_data_path = self.custom_config["arps_data_path"]

    def before_exec(self):
        wrfrun_config = WRFRUN.config
        background_files = ["arps.hdf000000", "arps.hdfgrdbas"]

        wrfrun_config.check_wrfrun_context(True)
        wrfrun_config.WRFRUN_WORK_STATUS = "arps3dvar"
        WRFRUN.check_path(f"{self.work_path}/outputs")

        work_dir = WRFRUN.uri.parse_resource_uri(self.work_path)
        existing_files = listdir(work_dir)
        missing_background_files = [file_name for file_name in background_files if file_name not in existing_files]

        if missing_background_files:
            if self.arps_data_path is None:
                self.arps_data_path = f"{WRFRUN.uri.WRFRUN_OUTPUT_PATH}/arps"

            arps_data_path = WRFRUN.uri.parse_resource_uri(self.arps_data_path)
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

            self.add_input_files([f"{self.arps_data_path}/{file_name}" for file_name in missing_background_files])

        namelist_updates = {
            "jobname": {"runname": self.name},
            "initialization": {
                "inifile": "./arps.hdf000000",
                "inigbf": "./arps.hdfgrdbas",
            },
            "output": {"dirname": "./outputs/"},
        }
        if wrfrun_config.get_namelist("arps")["incr_out"]["incrdmp"] > 0:
            namelist_updates["incr_out"] = {"incdmpf": f"./outputs/{self.name}.incr"}

        wrfrun_config.update_namelist(namelist_updates, "arps")
        wrfrun_config.write_namelist(self.namelist_path, "arps")

        super().before_exec()

    def after_exec(self):
        if not WRFRUN.config.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.",
                output_dir=f"{self.work_path}/outputs",
                save_path=self._output_save_path,
            )
            self.add_output_files(
                filenames=[f"{self.name}.lst", f"{self.name}.adasstat", f"{self.name}.adasstn", "arps3dvar.nml"],
                output_dir=self.work_path,
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()

        LOGGER.info(f"All arps3dvar output files have been copied to {WRFRUN.uri.parse_resource_uri(self._output_save_path)}")


def _exec_register_func(exec_db: ExecutableDB):
    """
    Function to register ``Executable``.

    :param exec_db: ``ExecutableDB`` instance.
    :type exec_db: ExecutableDB
    """
    class_list = [ARPSSFC, ARPS, ARPS3DVar, EXT2ARPS]
    class_id_list = ["arpssfc", "arps", "arps3dvar", "ext2arps"]

    for _class, _id in zip(class_list, class_id_list):
        if not exec_db.is_registered(_id):
            exec_db.register_exec(_id, _class)


WRFRUN.set_exec_db_register_func(_exec_register_func)


__all__ = ["ARPSSFC", "ARPS", "ARPS3DVar", "EXT2ARPS"]
