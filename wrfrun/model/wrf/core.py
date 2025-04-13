from os import listdir
from os.path import basename, exists
from typing import Optional, Union

from wrfrun.core import FileConfigDict, InputFileError, WRFRUNConfig
from wrfrun.utils import logger
from ..base import ModelExecutableBase, NamelistName
from ..dutils import VtableFiles
from ..utils import reconcile_namelist_metgrid


class GeoGrid(ModelExecutableBase):
    """
    Execute "geogrid.exe".
    """

    def __init__(self, geogrid_tbl_file: Optional[str] = None, core_num: Optional[int] = None):
        """
        Execute "geogrid.exe".

        :param geogrid_tbl_file: Custom GEOGRID.TBL file path. Defaults to None.
        :type geogrid_tbl_file: str
        :param core_num: An positive integer number of used core numbers. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
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

        super().__init__(name="geogrid", cmd="./geogrid.exe", work_path=WRFRUNConfig.WPS_WORK_PATH, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.geogrid_tbl_file = geogrid_tbl_file

    def generate_custom_config(self):
        """
        Get and store namelist.
        :return:
        :rtype:
        """
        super().generate_custom_config()
        self.custom_config["geogrid_tbl_file"] = self.geogrid_tbl_file

    def load_custom_config(self):
        super().load_custom_config()
        self.geogrid_tbl_file = self.custom_config["geogrid_tbl_file"]

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "geogrid"

        if self.geogrid_tbl_file:
            tbl_file: FileConfigDict = {"file_path": self.geogrid_tbl_file, "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/geogrid", "save_name": "GEOGRID.TBL", "is_data": False}
            self.add_input_files(tbl_file)

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}", "wps")

    def after_exec(self):
        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/geogrid"
        log_save_path = f"{output_path}/geogrid/logs"
        self.add_output_files(save_path=log_save_path, startswith="geogrid.log", outputs=NamelistName.WPS)
        self.add_output_files(save_path=output_save_path, startswith="geo_em")

        super().after_exec()

        logger.info(f"All geogrid output files have been copied to {output_save_path}")


class LinkGrib(ModelExecutableBase):
    """
    Run command: "./link_grib.csh".
    """

    def __init__(self, grib_dir_path: str):
        """
        Execute "link_grib.csh".

        :param grib_dir_path: GRIB data path. Relative path is recommended, because it will have better compatibility when you use the replay feature.
        :type grib_dir_path: str
        """
        self._link_grib_input_path = "./input_grib_data_dir"

        super().__init__(name="link_grib", cmd=["./link_grib.csh", f"{self._link_grib_input_path}/*", "."], work_path=WRFRUNConfig.WPS_WORK_PATH)

        self.grib_dir_path = grib_dir_path

    def generate_custom_config(self):
        self.class_config["class_args"] = (self.grib_dir_path,)

    def replay(self):
        self()

    def before_exec(self):
        grib_dir_path = WRFRUNConfig.parse_wrfrun_uri(self.grib_dir_path)

        if not exists(grib_dir_path):
            logger.error(f"GRIB file directory not found: {grib_dir_path}")
            raise FileNotFoundError(f"GRIB file directory not found: {grib_dir_path}")

        for _file in listdir(grib_dir_path):
            self.add_input_files(
                {
                    "file_path": f"{self.grib_dir_path}/{_file}",
                    "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/{self._link_grib_input_path}",
                    "save_name": _file, "is_data": True
                }
            )

        super().before_exec()


class UnGrib(ModelExecutableBase):
    """
    Execute "ungrib.exe".
    """

    def __init__(self, vtable_file: Optional[str] = None, input_data_path: Optional[str] = None):
        """
        Execute "ungrib.exe".

        :param vtable_file: Path of the Vtable file "ungrib.exe" used.
        :type vtable_file: str
        :param input_data_path: Path of the directory stores input GRIB2 files.
        :type input_data_path: str
        """
        super().__init__(name="ungrib", cmd="./ungrib.exe", work_path=WRFRUNConfig.WPS_WORK_PATH)

        self.vtable_file = vtable_file
        self.input_data_path = input_data_path

    def call_link_grib(self):
        """
        Execute "link_grib.csh" if needed.

        :return:
        :rtype:
        """
        if self.input_data_path is None:
            self.input_data_path = WRFRUNConfig.get_wrf_config()["wps_input_data_folder"]

        else:
            if not exists(self.input_data_path):
                logger.error(f"Can not find input data: {self.input_data_path}")
                raise FileNotFoundError(f"Can not find input data: {self.input_data_path}")

        LinkGrib(self.input_data_path)()

    def generate_custom_config(self):
        """
        Get and store namelist.

        :return:
        :rtype:
        """
        super().generate_custom_config()
        self.custom_config["vtable_file"] = self.vtable_file

    def load_custom_config(self):
        super().load_custom_config()
        self.vtable_file = self.custom_config["vtable_file"]

    def replay(self):
        super().__call__()

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "ungrib"

        if self.vtable_file is None:
            self.vtable_file = VtableFiles.ERA_PL

        self.add_input_files(
            {
                "file_path": self.vtable_file,
                "save_path": WRFRUNConfig.WPS_WORK_PATH,
                "save_name": "Vtable",
                "is_data": False
            }
        )

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}", "wps")

    def after_exec(self):
        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/ungrib"
        log_save_path = f"{output_path}/ungrib/logs"
        self.add_output_files(output_dir=WRFRUNConfig.get_ungrib_out_dir_path(), save_path=output_save_path, startswith=WRFRUNConfig.get_ungrib_out_prefix())
        self.add_output_files(save_path=log_save_path, outputs=["ungrib.log", "namelist.wps"])

        super().after_exec()

        logger.info(f"All geogrid output files have been copied to {output_save_path}")

    def __call__(self):
        self.call_link_grib()

        super().__call__()


class MetGrid(ModelExecutableBase):
    """
    Execute "metgrid.exe".
    """

    def __init__(self, geogrid_data_path: Optional[str] = None, ungrib_data_path: Optional[str] = None, core_num: Optional[int] = None):
        """
        Execute "metgrid.exe".

        :param geogrid_data_path: Directory path of outputs from geogrid.exe. If None, tries to use the output path specified by config file.
        :type geogrid_data_path: str
        :param ungrib_data_path: Directory path of outputs from ungrib.exe. If None, tries to use the output path specified by config file.
        :type ungrib_data_path: str
        :param core_num: An positive integer number of used core numbers. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
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

        super().__init__(name="metgrid", cmd="./metgrid.exe", work_path=WRFRUNConfig.WPS_WORK_PATH, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.geogrid_data_path = geogrid_data_path
        self.ungrib_data_path = ungrib_data_path

    def generate_custom_config(self):
        """
        Get and store namelist.
        :return:
        :rtype:
        """
        self.custom_config.update(
            {
                "geogrid_data_path": self.geogrid_data_path,
                "ungrib_data_path": self.ungrib_data_path,
            }
        )

    def load_custom_config(self):
        super().load_custom_config()
        self.geogrid_data_path = self.custom_config["geogrid_data_path"]
        self.ungrib_data_path = self.custom_config["ungrib_data_path"]

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "metgrid"

        # check input of metgrid.exe
        # try to search input files in the output path if workspace is clear.
        file_list = listdir(WRFRUNConfig.parse_wrfrun_uri(WRFRUNConfig.WPS_WORK_PATH))

        if "geo_em.d01.nc" not in file_list:

            if self.geogrid_data_path is None:
                self.geogrid_data_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/geogrid"
            geogrid_data_path = WRFRUNConfig.parse_wrfrun_uri(self.geogrid_data_path)

            if not exists(geogrid_data_path) or "geo_em.d01.nc" not in listdir(geogrid_data_path):
                logger.error(f"Can't find geogrid outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")
                raise FileNotFoundError(f"Can't find geogrid outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")

            else:
                geogrid_file_list = [x for x in listdir(geogrid_data_path) if x.startswith("geo_em.d")]
                for _file in geogrid_file_list:
                    self.add_input_files(
                        {
                            "file_path": f"{self.geogrid_data_path}/{_file}",
                            "save_path": WRFRUNConfig.WPS_WORK_PATH,
                            "save_name": _file,
                            "is_data": True
                        }
                    )

        ungrib_output_dir = WRFRUNConfig.parse_wrfrun_uri(WRFRUNConfig.get_ungrib_out_dir_path())
        if basename(ungrib_output_dir) not in file_list or len(listdir(ungrib_output_dir)) == 0:

            if self.ungrib_data_path is None:
                self.ungrib_data_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/ungrib"

            ungrib_data_path = WRFRUNConfig.parse_wrfrun_uri(self.ungrib_data_path)

            if not exists(ungrib_data_path) or len(listdir(ungrib_data_path)) == 0:
                logger.error(f"Can't find ungrib outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")
                raise FileNotFoundError(f"Can't find ungrib outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")

            else:
                ungrib_file_list = [x for x in listdir(ungrib_data_path)]
                for _file in ungrib_file_list:
                    self.add_input_files(
                        {
                            "file_path": f"{self.ungrib_data_path}/{_file}",
                            "save_path": WRFRUNConfig.get_ungrib_out_dir_path(),
                            "save_name": _file,
                            "is_data": True
                        }
                    )

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}", "wps")

    def after_exec(self):
        output_save_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/metgrid"
        log_save_path = f"{output_save_path}/logs"
        self.add_output_files(save_path=log_save_path, startswith="metgrid.log", outputs="namelist.wps")
        self.add_output_files(save_path=output_save_path, startswith="met_em")

        super().after_exec()

        logger.info(f"All metgrid output files have been copied to {output_save_path}")


class Real(ModelExecutableBase):
    """
    Execute "real.exe".
    """

    def __init__(self, metgrid_data_path: Optional[str] = None, core_num: Optional[int] = None):
        """
        Execute "real.exe".

        :param metgrid_data_path: Path of the directory stores outputs from "metgrid.exe".
        :type metgrid_data_path: str
        :param core_num: An positive integer number of used core numbers. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
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

        super().__init__(name="real", cmd="./real.exe", work_path=WRFRUNConfig.WRF_WORK_PATH, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.metgrid_data_path = metgrid_data_path

    def generate_custom_config(self):
        super().generate_custom_config()
        self.custom_config["metgrid_data_path"] = self.metgrid_data_path

    def load_custom_config(self):
        super().load_custom_config()
        self.metgrid_data_path = self.custom_config["metgrid_data_path"]

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "real"

        if self.metgrid_data_path is None:
            self.metgrid_data_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/metgrid"

        metgrid_data_path = WRFRUNConfig.parse_wrfrun_uri(self.metgrid_data_path)
        reconcile_namelist_metgrid(metgrid_data_path)

        file_list = [x for x in listdir(metgrid_data_path) if x.startswith("met_em")]
        for _file in file_list:
            self.add_input_files(
                {
                    "file_path": f"{self.metgrid_data_path}/{_file}",
                    "save_path": WRFRUNConfig.WRF_WORK_PATH,
                    "save_name": _file,
                    "is_data": True
                }
            )

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WRF_WORK_PATH}/{NamelistName.WRF}", "wrf")

    def after_exec(self):
        output_save_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/real"
        log_save_path = f"{output_save_path}/logs"

        self.add_output_files(save_path=output_save_path, startswith=("wrfbdy", "wrfinput", "wrflow"))
        self.add_output_files(save_path=log_save_path, startswith="rsl.", outputs="namelist.input")

        super().after_exec()

        logger.info(f"All real output files have been copied to {output_save_path}")


class WRF(ModelExecutableBase):
    """
    Execute "wrf.exe".
    """
    def __init__(self, input_file_dir_path: Optional[str] = None, restart_file_dir_path: Optional[str] = None, save_restarts=False, core_num: Optional[int] = None):
        """
        Execute "wrf.exe"

        :param input_file_dir_path: Path of the directory that stores input data for "wrf.exe".
        :type input_file_dir_path: str
        :param restart_file_dir_path: Path of the directory that stores restart files for "wrf.exe".
        :type restart_file_dir_path: str
        :param save_restarts: If saving restart files from "wrf.exe". Defaults to False.
        :type save_restarts: bool
        :param core_num: An positive integer number of used core numbers. ``mpirun`` will be used to execute geogrid.exe if ``core_num != None``.
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

        super().__init__(name="wrf", cmd="./wrf.exe", work_path=WRFRUNConfig.WRF_WORK_PATH, mpi_use=mpi_use, mpi_cmd=mpi_cmd, mpi_core_num=mpi_core_num)

        self.input_file_dir_path = input_file_dir_path
        self.restart_file_dir_path = restart_file_dir_path
        self.save_restarts = save_restarts

    def generate_custom_config(self):
        super().generate_custom_config()
        self.custom_config.update({
            "input_file_dir_path": self.input_file_dir_path,
            "restart_file_dir_path": self.restart_file_dir_path,
            "save_restarts": self.save_restarts
        })

    def load_custom_config(self):
        super().load_custom_config()
        self.input_file_dir_path = self.custom_config["input_file_dir_path"]
        self.restart_file_dir_path = self.custom_config["restart_file_dir_path"]
        self.save_restarts = self.custom_config["save_restarts"]

    def before_exec(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "wrf"

        if self.input_file_dir_path is None:
            self.input_file_dir_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/real"

        input_file_dir_path = WRFRUNConfig.parse_wrfrun_uri(self.input_file_dir_path)

        if exists(input_file_dir_path):
            file_list = [x for x in listdir(input_file_dir_path) if x != "logs"]

            for _file in file_list:
                self.add_input_files(
                    {
                        "file_path": f"{self.input_file_dir_path}/{_file}",
                        "save_path": WRFRUNConfig.WRF_WORK_PATH,
                        "save_name": _file,
                        "is_data": True
                    }
                )

        if WRFRUNConfig.is_restart():
            if self.restart_file_dir_path is None:
                logger.error("You need to specify the restart file if you want to restart WRF.")
                raise InputFileError("You need to specify the restart file if you want to restart WRF.")

            restart_file_dir_path = WRFRUNConfig.parse_wrfrun_uri(self.restart_file_dir_path)

            if not exists(restart_file_dir_path):
                logger.error(f"Restart files not found: {restart_file_dir_path}")
                raise FileNotFoundError(f"Restart files not found: {restart_file_dir_path}")

            file_list = [x for x in listdir(restart_file_dir_path) if x.startswith("wrfrst")]
            for _file in file_list:
                self.add_input_files(
                    {
                        "file_path": f"{self.restart_file_dir_path}/{_file}",
                        "save_path": WRFRUNConfig.WRF_WORK_PATH,
                        "save_name": _file,
                        "is_data": True
                    }
                )

        super().before_exec()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WRF_WORK_PATH}/{NamelistName.WRF}", "wrf")

    def after_exec(self):
        output_save_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/wrf"
        log_save_path = f"{output_save_path}/logs"

        self.add_output_files(save_path=log_save_path, startswith="rsl.", outputs="namelist.input")
        self.add_output_files(save_path=output_save_path, startswith="wrfout")
        if self.save_restarts:
            restart_save_path = f"{output_save_path}/restart"
            self.add_output_files(save_path=restart_save_path, startswith="wrfrst", no_file_error=False)

        super().after_exec()

        logger.info(f"All wrf output files have been copied to {output_save_path}")


def geogrid(geogrid_tbl_file: Union[str, None] = None):
    """
    Interface to execute geogrid.exe.

    :param geogrid_tbl_file: Custom GEOGRID.TBL file path. Defaults to None.
    """
    GeoGrid(geogrid_tbl_file, WRFRUNConfig.get_pbs_core_num())()


def ungrib(vtable_file: Union[str, None] = None, input_data_path: Optional[str] = None):
    """
    Interface to execute ungrib.exe.

    :param vtable_file: Vtable file used to run ungrib. Defaults to None.
    :param input_data_path: Directory path of the input data. If None, ``wrfrun`` will read its value from the config file.
    """
    UnGrib(vtable_file, input_data_path)()


def metgrid(geogrid_data_path: Optional[str] = None, ungrib_data_path: Optional[str] = None):
    """
    Interface to execute metgrid.exe.

    :param geogrid_data_path: Directory path of outputs from geogrid.exe. If None, tries to use the output path specified by config file.
    :type geogrid_data_path: str
    :param ungrib_data_path: Directory path of outputs from ungrib.exe. If None, tries to use the output path specified by config file.
    :type ungrib_data_path: str
    """
    MetGrid(geogrid_data_path, ungrib_data_path, WRFRUNConfig.get_pbs_core_num())()


def real(metgrid_data_path: Union[str, None] = None):
    """
    Interface to execute real.exe.

    :param metgrid_data_path: The path store output from metgrid.exe. If it is None, the default output path will be used.
    """
    Real(metgrid_data_path, WRFRUNConfig.get_pbs_core_num())()


def wrf(input_file_dir_path: Union[str, None] = None, restart_file_dir_path: Optional[str] = None, save_restarts=False):
    """
    Interface to execute wrf.exe.

    :param input_file_dir_path: The path store input data which will be feed into wrf.exe. Defaults to None.
    :param restart_file_dir_path: The path store WRF restart files. This parameter will be ignored if ``restart=False`` in your config.
    :param save_restarts: Also save restart files to the output directory.
    """
    WRF(input_file_dir_path, restart_file_dir_path, save_restarts, WRFRUNConfig.get_pbs_core_num())()


__all__ = ["GeoGrid", "LinkGrib", "UnGrib", "MetGrid", "Real", "WRF", "geogrid", "ungrib", "metgrid", "real", "wrf"]
