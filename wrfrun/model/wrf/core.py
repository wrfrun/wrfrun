"""
wrfrun.model.wrf.core
#####################

Core implementation of WRF model. All ``Executable`` of WPS / WRF model are defined here.

If you prefer function interfaces, please see :doc:`function wrapper </api/model.wrf.exec_wrap>` for these ``Executable``.

.. autosummary::
    :toctree: generated/

    GeoGrid
    LinkGrib
    UnGrib
    MetGrid
    Real
    WRF
    DFI
    NDown
"""

from os import listdir
from os.path import abspath, basename, exists
from shutil import copyfile, move, rmtree
from typing import Optional, Union

from wrfrun.core import ExecutableBase, FileConfigDict, InputFileError, NamelistIDError, WRFRUNConfig, WRFRUNExecDB
from wrfrun.workspace.wrf import WORKSPACE_MODEL_WPS, WORKSPACE_MODEL_WRF
from wrfrun.utils import logger
from .utils import reconcile_namelist_metgrid, process_after_ndown
from .namelist import (prepare_dfi_namelist, prepare_wps_namelist, prepare_wrf_namelist,
                       prepare_wrfda_namelist, get_ungrib_out_dir_path, get_ungrib_out_prefix,
                       set_ungrib_out_prefix, set_metgrid_fg_names)
from .vtable import VtableFiles
from ..base import NamelistName


def _check_and_prepare_namelist():
    """
    This function check if namelists needed by WPS/WRF have been loaded,
    and prepare namelist if check fails.
    """
    if not WRFRUNConfig.check_namelist("wps"):
        prepare_wps_namelist()

    if not WRFRUNConfig.check_namelist("wrf"):
        prepare_wrf_namelist()

    if not WRFRUNConfig.check_namelist("wrfda"):
        prepare_wrfda_namelist()


class GeoGrid(ExecutableBase):
    """
    ``Executable`` for "geogrid.exe".
    """

    def __init__(self, geogrid_tbl_file: Optional[str] = None, core_num: Optional[int] = None):
        """
        ``Executable`` for "geogrid.exe".

        :param geogrid_tbl_file: Custom GEOGRID.TBL file path. Defaults to None.
        :type geogrid_tbl_file: str
        :param core_num: An positive integer number. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
        :type core_num: int
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning(f"`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        super().__init__(name="geogrid", cmd="./geogrid.exe", work_path=WORKSPACE_MODEL_WPS, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.geogrid_tbl_file = geogrid_tbl_file

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Namelist settings.
        2. Path of custom TBL file.
        """
        self.custom_config.update(
            {
                "namelist": WRFRUNConfig.get_namelist("wps"),
                "geogrid_tbl_file": self.geogrid_tbl_file
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wps")
        self.geogrid_tbl_file = self.custom_config["geogrid_tbl_file"]

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "geogrid"

        if not WRFRUNConfig.IS_IN_REPLAY:
            if self.geogrid_tbl_file is not None:
                tbl_file: FileConfigDict = {
                    "file_path": self.geogrid_tbl_file, "save_path": f"{WORKSPACE_MODEL_WPS}/geogrid",
                    "save_name": "GEOGRID.TBL", "is_data": False, "is_output": False
                }
                self.add_input_files(tbl_file)

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WPS}/{NamelistName.WPS}", "wps")

        # print debug logs
        logger.debug("Namelist settings of 'geogrid':")
        logger.debug(WRFRUNConfig.get_namelist("wps"))

    def after_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:
            self.add_output_files(save_path=self._log_save_path, startswith="geogrid.log", outputs=NamelistName.WPS)
            self.add_output_files(save_path=self._output_save_path, startswith="geo_em")

        super().after_exec()

        logger.info(f"All geogrid output files have been copied to {WRFRUNConfig.parse_resource_uri(self._output_save_path)}")


class LinkGrib(ExecutableBase):
    """
    ``Executable`` for "./link_grib.csh".
    """

    def __init__(self, grib_dir_path: str):
        """
        ``Executable`` for "link_grib.csh".

        :param grib_dir_path: GRIB data directory path. Absolute path is recommended.
        :type grib_dir_path: str
        """
        self._link_grib_input_path = "./input_grib_data_dir"

        super().__init__(name="link_grib", cmd=["./link_grib.csh", f"{self._link_grib_input_path}/*", "."], work_path=WORKSPACE_MODEL_WPS)
        self.grib_dir_path = grib_dir_path

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Positional arguments of this ``Executable``.
        """
        self.class_config["class_args"] = (self.grib_dir_path,)

    def before_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:

            logger.debug(f"Input data are: {self.grib_dir_path}")
            _grib_dir_path = abspath(self.grib_dir_path)

            if not exists(_grib_dir_path):
                logger.error(f"GRIB file directory not found: {_grib_dir_path}")
                raise FileNotFoundError(f"GRIB file directory not found: {_grib_dir_path}")

            save_path = f"{WORKSPACE_MODEL_WPS}/{self._link_grib_input_path}"
            save_path = WRFRUNConfig.parse_resource_uri(save_path)
            if exists(save_path):
                rmtree(save_path)

            for _file in listdir(_grib_dir_path):
                _file_config: FileConfigDict = {
                    "file_path": f"{_grib_dir_path}/{_file}",
                    "save_path": f"{WORKSPACE_MODEL_WPS}/{self._link_grib_input_path}",
                    "save_name": _file, "is_data": True, "is_output": False,
                }
                self.add_input_files(_file_config)

        super().before_exec()


class UnGrib(ExecutableBase):
    """
    ``Executable`` for "ungrib.exe".
    """

    def __init__(self, vtable_file: Optional[str] = None, input_data_path: Optional[str] = None):
        """
        ``Executable`` for "ungrib.exe".

        :param vtable_file: Path of the Vtable file.
                            Defaults to :attr:`VtableFiles.ERA_PL <vtable.VtableFiles.ERA_PL>`.
        :type vtable_file: str
        :param input_data_path: Directory path of input GRIB files.
                                Defaults to ``input_data_path`` set in user's config file.
        :type input_data_path: str
        """
        super().__init__(name="ungrib", cmd="./ungrib.exe", work_path=WORKSPACE_MODEL_WPS)

        self.vtable_file = vtable_file
        self.input_data_path = input_data_path

        _check_and_prepare_namelist()

    def call_link_grib(self):
        """
        Call :class:`LinkGrib` if needed.
        """
        if self.input_data_path is None:
            self.input_data_path = WRFRUNConfig.get_input_data_path()

        LinkGrib(self.input_data_path)()

    def set_ungrib_output_prefix(self, prefix="FILE") -> "UnGrib":
        """
        This method is the same as :func:`set_ungrib_output_prefix <wrfrun.model.wrf.namelist.set_ungrib_output_prefix>`.
        ``wrfrun`` provide this method to avoid changing namelist before loading it.

        :param prefix: Prefix of outputs.
        :type prefix: str
        :return: This instance itself.
        :rtype: UnGrib
        """
        prefix = basename(prefix)
        set_ungrib_out_prefix(prefix)
        return self

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Namelist settings.
        2. Path of used VTable file.
        """
        self.custom_config.update(
            {
                "namelist": WRFRUNConfig.get_namelist("wps"),
                "vtable_file": self.vtable_file
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        self.vtable_file = self.custom_config["vtable_file"]
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wps")

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "ungrib"

        if not WRFRUNConfig.IS_IN_REPLAY:
            if self.vtable_file is None:
                self.vtable_file = VtableFiles.ERA_PL

            _file_config: FileConfigDict = {
                "file_path": self.vtable_file,
                "save_path": WORKSPACE_MODEL_WPS,
                "save_name": "Vtable",
                "is_data": False,
                "is_output": False
            }
            self.add_input_files(_file_config)

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WPS}/{NamelistName.WPS}", "wps")

        # print debug logs
        logger.debug("Namelist settings of 'ungrib':")
        logger.debug(WRFRUNConfig.get_namelist("wps"))

    def after_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:
            self.add_output_files(output_dir=get_ungrib_out_dir_path(), save_path=self._output_save_path, startswith=get_ungrib_out_prefix())
            self.add_output_files(save_path=self._log_save_path, outputs=["ungrib.log", "namelist.wps"])

        super().after_exec()

        logger.info(f"All ungrib output files have been copied to {WRFRUNConfig.parse_resource_uri(self._output_save_path)}")

    def __call__(self):
        self.call_link_grib()

        super().__call__()


class MetGrid(ExecutableBase):
    """
    ``Executable`` of "metgrid.exe".
    """

    def __init__(self, geogrid_data_path: Optional[str] = None, ungrib_data_path: Optional[str] = None, core_num: Optional[int] = None):
        """
        ``Executable`` of "metgrid.exe".

        :param geogrid_data_path: Directory path of :class:`GeoGrid` outputs.
                                  If is ``None``, try to use the output path specified by config file.
        :type geogrid_data_path: str
        :param ungrib_data_path: Directory path of :class:`UnGrib` outputs.
                                 If is ``None``, try to use the output path specified by config file.
        :type ungrib_data_path: str
        :param core_num: An positive integer number. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
        :type core_num: int
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning(f"`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        super().__init__(name="metgrid", cmd="./metgrid.exe", work_path=WORKSPACE_MODEL_WPS, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.geogrid_data_path = geogrid_data_path
        self.ungrib_data_path = ungrib_data_path

        _check_and_prepare_namelist()

    def set_metgrid_fg_names(self, fg_names: Union[str, list[str]] = "FILE") -> "MetGrid":
        """
        This method
        :param fg_names: ``fg_name`` of metgrid, a single prefix string or a string list.
        :type fg_names: str | list
        :return: This instance itself.
        :rtype: MetGrid
        """
        if isinstance(fg_names, str):
            fg_names = [fg_names, ]
        fg_names = [basename(x) for x in fg_names]
        set_metgrid_fg_names(fg_names)
        return self

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Directory path of :class:`GeoGrid` outputs.
        2. Directory path of :class:`UnGrib` outputs.
        3. Namelist settings.
        """
        self.custom_config.update(
            {
                "geogrid_data_path": self.geogrid_data_path,
                "ungrib_data_path": self.ungrib_data_path,
                "namelist": WRFRUNConfig.get_namelist("wps"),
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        self.geogrid_data_path = self.custom_config["geogrid_data_path"]
        self.ungrib_data_path = self.custom_config["ungrib_data_path"]
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wps")

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "metgrid"

        if not WRFRUNConfig.IS_IN_REPLAY and not WRFRUNConfig.FAKE_SIMULATION_MODE:
            # check input of metgrid.exe
            # try to search input files in the output path if workspace is clear.
            file_list = listdir(WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WPS))

            if "geo_em.d01.nc" not in file_list:

                if self.geogrid_data_path is None:
                    self.geogrid_data_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/geogrid"
                geogrid_data_path = WRFRUNConfig.parse_resource_uri(self.geogrid_data_path)

                if not exists(geogrid_data_path) or "geo_em.d01.nc" not in listdir(geogrid_data_path):
                    logger.error(f"Can't find geogrid outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")
                    raise FileNotFoundError(f"Can't find geogrid outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")

                else:
                    geogrid_file_list = [x for x in listdir(geogrid_data_path) if x.startswith("geo_em.d")]
                    for _file in geogrid_file_list:
                        _file_config = {
                            "file_path": f"{self.geogrid_data_path}/{_file}",
                            "save_path": WORKSPACE_MODEL_WPS,
                            "save_name": _file,
                            "is_data": True,
                            "is_output": True
                        }
                        self.add_input_files(_file_config)

            ungrib_output_dir = WRFRUNConfig.parse_resource_uri(get_ungrib_out_dir_path())
            if basename(ungrib_output_dir) not in file_list or len(listdir(ungrib_output_dir)) == 0:

                if self.ungrib_data_path is None:
                    self.ungrib_data_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/ungrib"

                ungrib_data_path = WRFRUNConfig.parse_resource_uri(self.ungrib_data_path)

                if not exists(ungrib_data_path) or len(listdir(ungrib_data_path)) == 0:
                    logger.error(f"Can't find ungrib outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")
                    raise FileNotFoundError(f"Can't find ungrib outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")

                else:
                    ungrib_file_list = [x for x in listdir(ungrib_data_path)]
                    for _file in ungrib_file_list:
                        _file_config: FileConfigDict = {
                            "file_path": f"{self.ungrib_data_path}/{_file}",
                            "save_path": get_ungrib_out_dir_path(),
                            "save_name": _file,
                            "is_data": True,
                            "is_output": True
                        }
                        self.add_input_files(_file_config)

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WPS}/{NamelistName.WPS}", "wps")

    def after_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:
            self.add_output_files(save_path=self._log_save_path, startswith="metgrid.log", outputs="namelist.wps")
            self.add_output_files(save_path=self._output_save_path, startswith="met_em")

        super().after_exec()

        logger.info(f"All metgrid output files have been copied to {WRFRUNConfig.parse_resource_uri(self._output_save_path)}")


class Real(ExecutableBase):
    """
    ``Executable`` of "real.exe".
    """

    def __init__(self, metgrid_data_path: Optional[str] = None, core_num: Optional[int] = None):
        """
        ``Executable`` of "real.exe".

        :param metgrid_data_path: Directory path of :class:`MetGrid` outputs.
                                  If is ``None``, try to use the workspace path or output path in the config file.
        :type metgrid_data_path: str
        :param core_num: An positive integer number. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
        :type core_num: int
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning(f"`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        _check_and_prepare_namelist()

        super().__init__(name="real", cmd="./real.exe", work_path=WORKSPACE_MODEL_WRF, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.metgrid_data_path = metgrid_data_path

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Namelist settings.
        2. Directory path of :class:`MetGrid` outputs.
        """
        self.custom_config["metgrid_data_path"] = self.metgrid_data_path
        self.custom_config.update(
            {
                "namelist": WRFRUNConfig.get_namelist("wrf"),
                "metgrid_data_path": self.metgrid_data_path
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        self.metgrid_data_path = self.custom_config["metgrid_data_path"]
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wrf")

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "real"

        if not WRFRUNConfig.IS_IN_REPLAY and not WRFRUNConfig.FAKE_SIMULATION_MODE:
            if self.metgrid_data_path is None:
                self.metgrid_data_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/metgrid"

            metgrid_data_path = WRFRUNConfig.parse_resource_uri(self.metgrid_data_path)
            reconcile_namelist_metgrid(metgrid_data_path)

            file_list = [x for x in listdir(metgrid_data_path) if x.startswith("met_em")]
            for _file in file_list:
                _file_config: FileConfigDict = {
                    "file_path": f"{self.metgrid_data_path}/{_file}",
                    "save_path": WORKSPACE_MODEL_WRF,
                    "save_name": _file,
                    "is_data": True,
                    "is_output": True
                }
                self.add_input_files(_file_config)

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WRF}/{NamelistName.WRF}", "wrf")

    def after_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:
            self.add_output_files(save_path=self._output_save_path, startswith=("wrfbdy", "wrfinput", "wrflow"))
            self.add_output_files(save_path=self._log_save_path, startswith="rsl.", outputs="namelist.input")

        super().after_exec()

        logger.info(f"All real output files have been copied to {WRFRUNConfig.parse_resource_uri(self._output_save_path)}")


class WRF(ExecutableBase):
    """
    ``Executable`` of "wrf.exe".
    """

    def __init__(self, input_file_dir_path: Optional[str] = None, restart_file_dir_path: Optional[str] = None, save_restarts=False, core_num: Optional[int] = None):
        """
        ``Executable`` of "wrf.exe"

        :param input_file_dir_path: Directory path of input data.
        :type input_file_dir_path: str
        :param restart_file_dir_path: Directory path of restart files.
        :type restart_file_dir_path: str
        :param save_restarts: If saving restart files. Defaults to False.
        :type save_restarts: bool
        :param core_num: An positive integer number. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
        :type core_num: int
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning(f"`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        _check_and_prepare_namelist()

        super().__init__(name="wrf", cmd="./wrf.exe", work_path=WORKSPACE_MODEL_WRF, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.input_file_dir_path = input_file_dir_path
        self.restart_file_dir_path = restart_file_dir_path
        self.save_restarts = save_restarts

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Directory path of input datas.
        2. Directory path of restart files.
        3. Namelist settings.
        """
        self.custom_config.update(
            {
                "input_file_dir_path": self.input_file_dir_path,
                "restart_file_dir_path": self.restart_file_dir_path,
                "namelist": WRFRUNConfig.get_namelist("wrf")
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        self.input_file_dir_path = self.custom_config["input_file_dir_path"]
        self.restart_file_dir_path = self.custom_config["restart_file_dir_path"]
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wrf")

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        # help wrfrun to make sure the input file is from real or ndown.
        last_work_status = WRFRUNConfig.WRFRUN_WORK_STATUS
        if last_work_status not in ["real", "ndown"]:
            last_work_status = ""
        WRFRUNConfig.WRFRUN_WORK_STATUS = "wrf"

        if not WRFRUNConfig.IS_IN_REPLAY and not WRFRUNConfig.FAKE_SIMULATION_MODE:
            if self.input_file_dir_path is None:
                if last_work_status == "":
                    # assume we already have outputs from real.exe.
                    self.input_file_dir_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/real"
                    is_output = False
                else:
                    self.input_file_dir_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/{last_work_status}"
                    is_output = True

            else:
                is_output = False

            input_file_dir_path = WRFRUNConfig.parse_resource_uri(self.input_file_dir_path)

            if exists(input_file_dir_path):
                file_list = [x for x in listdir(input_file_dir_path) if x != "logs"]

                for _file in file_list:
                    _file_config: FileConfigDict = {
                        "file_path": f"{self.input_file_dir_path}/{_file}",
                        "save_path": WORKSPACE_MODEL_WRF,
                        "save_name": _file,
                        "is_data": True,
                        "is_output": is_output
                    }
                    self.add_input_files(_file_config)

            if WRFRUNConfig.get_model_config("wrf")["restart_mode"]:
                if self.restart_file_dir_path is None:
                    logger.error("You need to specify the restart file if you want to restart WRF.")
                    raise InputFileError("You need to specify the restart file if you want to restart WRF.")

                restart_file_dir_path = WRFRUNConfig.parse_resource_uri(self.restart_file_dir_path)

                if not exists(restart_file_dir_path):
                    logger.error(f"Restart files not found: {restart_file_dir_path}")
                    raise FileNotFoundError(f"Restart files not found: {restart_file_dir_path}")

                file_list = [x for x in listdir(restart_file_dir_path) if x.startswith("wrfrst")]
                for _file in file_list:
                    _file_config: FileConfigDict = {
                        "file_path": f"{self.restart_file_dir_path}/{_file}",
                        "save_path": WORKSPACE_MODEL_WRF,
                        "save_name": _file,
                        "is_data": True,
                        "is_output": False
                    }
                    self.add_input_files(_file_config)

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WRF}/{NamelistName.WRF}", "wrf")

    def after_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:
            self.add_output_files(save_path=self._log_save_path, startswith="rsl.", outputs="namelist.input")
            self.add_output_files(save_path=self._output_save_path, startswith="wrfout")
            if self.save_restarts:
                restart_save_path = f"{self._output_save_path}/restart"
                self.add_output_files(save_path=restart_save_path, startswith="wrfrst", no_file_error=False)

        super().after_exec()

        logger.info(f"All wrf output files have been copied to {WRFRUNConfig.parse_resource_uri(self._output_save_path)}")


class DFI(ExecutableBase):
    """
    ``Executable`` to run DFI.
    """

    def __init__(self, input_file_dir_path: Optional[str] = None, update_real_output=True, core_num: Optional[int] = None):
        """
        ``Executable`` to run DFI.

        :param input_file_dir_path: Directory path of input data.
        :type input_file_dir_path: str
        :param update_real_output: If update corresponding files in :class:`Real` outputs.
        :type update_real_output: bool
        :param core_num: An positive integer number. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
        :type core_num: int
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning(f"`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        super().__init__(name="dfi", cmd="./wrf.exe", work_path=WORKSPACE_MODEL_WRF, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.input_file_dir_path = input_file_dir_path
        self.update_real_output = update_real_output

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Directory path of input datas.
        2. If update corresponding files in :class:`Real` outputs.
        3. Namelist settings.
        """
        self.custom_config.update(
            {
                "input_file_dir_path": self.input_file_dir_path,
                "update_real_output": self.update_real_output,
                "namelist": WRFRUNConfig.get_namelist("dfi")
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        self.input_file_dir_path = self.custom_config["input_file_dir_path"]
        self.update_real_output = self.custom_config["update_real_output"]

        if not WRFRUNConfig.register_custom_namelist_id("dfi"):
            logger.error("Can't register namelist for DFI.")
            raise NamelistIDError("Can't register namelist for DFI.")
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "dfi")

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "dfi"

        if not WRFRUNConfig.IS_IN_REPLAY and not WRFRUNConfig.FAKE_SIMULATION_MODE:
            # prepare config
            if self.input_file_dir_path is None:
                self.input_file_dir_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/real"
                is_output = True

            else:
                is_output = False

            input_file_dir_path = WRFRUNConfig.parse_resource_uri(self.input_file_dir_path)

            if exists(input_file_dir_path):
                file_list = [x for x in listdir(input_file_dir_path) if x != "logs"]

                for _file in file_list:
                    _file_config: FileConfigDict = {
                        "file_path": f"{self.input_file_dir_path}/{_file}",
                        "save_path": WORKSPACE_MODEL_WRF,
                        "save_name": _file,
                        "is_data": True,
                        "is_output": is_output
                    }
                    self.add_input_files(_file_config)

            if not WRFRUNConfig.register_custom_namelist_id("dfi"):
                logger.error("Can't register namelist for DFI.")
                raise NamelistIDError("Can't register namelist for DFI.")

            prepare_dfi_namelist()

        super().before_exec()
        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WRF}/{NamelistName.WRF}", "dfi")

    def after_exec(self):
        if not WRFRUNConfig.IS_IN_REPLAY:
            self.add_output_files(save_path=self._log_save_path, startswith="rsl.", outputs="namelist.input")
            self.add_output_files(save_path=self._output_save_path, startswith="wrfinput_initialized_")

        super().after_exec()

        parsed_output_save_path = WRFRUNConfig.parse_resource_uri(self._output_save_path)
        if self.update_real_output and not WRFRUNConfig.FAKE_SIMULATION_MODE:
            real_dir_path = WRFRUNConfig.parse_resource_uri(self.input_file_dir_path)

            move(f"{real_dir_path}/wrfinput_d01", f"{real_dir_path}/wrfinput_d01_before_dfi")
            copyfile(f"{parsed_output_save_path}/wrfinput_initialized_d01", f"{real_dir_path}/wrfinput_d01")
            logger.info(f"Replace real.exe output 'wrfinput_d01' with outputs, old file has been renamed as 'wrfinput_d01_before_dfi'")

        logger.info(f"All DFI output files have been copied to {parsed_output_save_path}")


class NDown(ExecutableBase):
    """
    ``Executable`` of "ndown.exe".
    """

    def __init__(self, wrfout_file_path: str, real_output_dir_path: Optional[str] = None, update_namelist=True, core_num: Optional[int] = None):
        """
        ``Executable`` of "ndown.exe".

        :param wrfout_file_path: wrfout file path.
        :type wrfout_file_path: str
        :param real_output_dir_path: Directory path of :class:`Real` outputs.
        :type real_output_dir_path: str
        :param update_namelist: If update namelist settings for the final integral.
        :type update_namelist: bool
        :param core_num: An positive integer number. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
        :type core_num: int
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning(f"`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        _check_and_prepare_namelist()

        super().__init__(name="ndown", cmd="./ndown.exe", work_path=WORKSPACE_MODEL_WRF, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.wrfout_file_path = wrfout_file_path
        self.real_output_dir_path = real_output_dir_path
        self.update_namelist = update_namelist

    def generate_custom_config(self):
        """
        Store custom configs, including:

        1. Positional arguments of this ``Executable``.
        2. Directory path of :class:`Real` outputs.
        3. If update namelist settings.
        4. Namelist settings.
        """
        self.class_config["class_args"] = (self.wrfout_file_path,)
        self.custom_config.update(
            {
                "real_output_dir_path": self.real_output_dir_path,
                "update_namelist": self.update_namelist,
                "namelist": WRFRUNConfig.get_namelist("wrf"),
            }
        )

    def load_custom_config(self):
        """
        Load custom configs.
        """
        self.real_output_dir_path = self.custom_config["real_output_dir_path"]
        self.update_namelist = self.custom_config["update_namelist"]
        WRFRUNConfig.update_namelist(self.custom_config["namelist"])

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "ndown"

        # we need to make sure time_control.io_form_auxinput2 is 2.
        # which means the format of input stream 2 is NetCDF.
        WRFRUNConfig.update_namelist({"time_control": {"io_form_auxinput2": 2}}, "wrf")

        if self.real_output_dir_path is None:
            self.real_output_dir_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/real"
            is_output = True

        else:
            is_output = False

        wrfndi_file_config: FileConfigDict = {
            "file_path": f"{self.real_output_dir_path}/wrfinput_d02",
            "save_path": WORKSPACE_MODEL_WRF,
            "save_name": "wrfndi_d02",
            "is_data": True,
            "is_output": is_output
        }
        wrfout_file_config: FileConfigDict = {
            "file_path": self.wrfout_file_path,
            "save_path": WORKSPACE_MODEL_WRF,
            "save_name": "wrfout_d01",
            "is_data": True,
            "is_output": False
        }

        self.add_input_files([wrfndi_file_config, wrfout_file_config])

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WORKSPACE_MODEL_WRF}/{NamelistName.WRF}", "wrf")

    def after_exec(self):
        self.add_output_files(save_path=self._log_save_path, startswith="rsl.", outputs="namelist.input")
        self.add_output_files(save_path=self._output_save_path, outputs=["wrfinput_d02", "wrfbdy_d02"])
        # also save other outputs of real.exe, so WRF can directly use them.
        self.add_output_files(output_dir=f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/real", save_path=self._output_save_path,
                              startswith="wrflowinp_", no_file_error=False)

        super().after_exec()

        parsed_output_save_path = WRFRUNConfig.parse_resource_uri(self._output_save_path)

        move(f"{parsed_output_save_path}/wrfinput_d02", f"{parsed_output_save_path}/wrfinput_d01")
        move(f"{parsed_output_save_path}/wrfbdy_d02", f"{parsed_output_save_path}/wrfbdy_d01")

        logger.info(f"All ndown output files have been copied to {parsed_output_save_path}")

        if self.update_namelist:
            process_after_ndown()


class_list = [GeoGrid, LinkGrib, UnGrib, MetGrid, Real, WRF, NDown]
class_id_list = ["geogrid", "link_grib", "ungrib", "metgrid", "real", "wrf", "ndown"]

for _class, _id in zip(class_list, class_id_list):
    if not WRFRUNExecDB.is_registered(_id):
        WRFRUNExecDB.register_exec(_id, _class)

__all__ = ["GeoGrid", "LinkGrib", "UnGrib", "MetGrid", "Real", "WRF", "DFI", "NDown"]
