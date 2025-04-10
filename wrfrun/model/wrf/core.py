from os import listdir, remove, symlink
from os.path import abspath, basename, exists
from typing import Optional

from wrfrun.core import ExecutableBase, WRFRUNConfig
from wrfrun.utils import check_path, logger
from ..base import FileConfigDict, ModelExecutableBase, NamelistName
from ..utils import VtableFiles, model_postprocess, model_preprocess


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

    def replay(self):
        self.before_call()
        super().__call__()
        self.after_call()

    def before_call(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "geogrid"

        # should only register the file in __call__, because we don't need to register again when replay the simulation.
        super().before_call()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}", "wps")

    def after_call(self):
        super().after_call()
        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/geogrid"
        logger.info(f"All geogrid output files have been copied to {output_save_path}")

    def __call__(self):
        if self.geogrid_tbl_file:
            tbl_file: FileConfigDict = {"file_path": self.geogrid_tbl_file, "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/geogrid", "save_name": "GEOGRID.TBL"}
            self.add_addition_files(tbl_file)

        self.before_call()
        self.generate_custom_config()

        super().__call__()

        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/geogrid"
        log_save_path = f"{output_path}/geogrid/logs"
        self.add_save_files(save_path=log_save_path, startswith="geogrid.log", outputs=NamelistName.WPS)
        self.add_save_files(save_path=output_save_path, startswith="geo_em")
        self.after_call()


class LinkGrib(ExecutableBase):
    """
    Run command: "./link_grib.csh".
    """
    def __init__(self, grib_dir_path: str):
        """
        Execute "link_grib.csh".

        :param grib_dir_path: GRIB data path. Relative path is recommended, because it will have better compatibility when you use the replay feature.
        :type grib_dir_path: str
        """
        super().__init__(name="link_grib", cmd=["./link_grib.csh", f"{abspath(grib_dir_path)}/*", "."], work_path=WRFRUNConfig.WPS_WORK_PATH)

        self.grib_dir_path = grib_dir_path

    def generate_custom_config(self):
        self.class_config["class_args"] = (self.grib_dir_path, )

    def load_custom_config(self):
        pass

    def replay(self):
        super().__call__()

    def __call__(self):
        if self.grib_dir_path is None:
            logger.error("You have to give a valid grib file path.")
            raise ValueError("You have to give a valid grib file path.")

        self.generate_custom_config()
        super().__call__()


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

    def before_call(self):
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "ungrib"

        # should only register the file in __call__, because we don't need to register again when replay the simulation.
        super().before_call()

        WRFRUNConfig.write_namelist(f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}", "wps")

    def after_call(self):
        super().after_call()
        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/ungrib"
        logger.info(f"All geogrid output files have been copied to {output_save_path}")

    def __call__(self):
        self.call_link_grib()

        WPS_WORK_PATH = WRFRUNConfig.WPS_WORK_PATH

        if self.vtable_file is not None:
            if self.vtable_file.startswith(":/"):
                vtable_file = self.vtable_file.strip(":/")
                vtable_file = f"{WPS_WORK_PATH}/ungrib/Variable_Tables/{vtable_file}"

            else:
                vtable_file = abspath(self.vtable_file)

        else:
            vtable_file = VtableFiles.ERA_PL.strip(":/")
            vtable_file = f"{WPS_WORK_PATH}/ungrib/Variable_Tables/{vtable_file}"

        vtable_file_config: FileConfigDict = {"file_path": vtable_file, "save_path": WPS_WORK_PATH, "save_name": "Vtable"}
        self.add_addition_files(vtable_file_config)

        self.before_call()
        self.generate_custom_config()

        super().__call__()

        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/ungrib"
        log_save_path = f"{output_path}/ungrib/logs"
        self.add_save_files(output_dir=WRFRUNConfig.get_ungrib_out_dir_path(), save_path=output_save_path, startswith=WRFRUNConfig.get_ungrib_out_prefix())
        self.add_save_files(save_path=log_save_path, outputs=["ungrib.log", "namelist.wps"])
        self.after_call()


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
        self.custom_config.update({
            "namelist": WRFRUNConfig.get_namelist("wps"),
            "geogrid_data_path": self.geogrid_data_path,
            "ungrib_data_path": self.ungrib_data_path,
        })

    def load_custom_config(self):
        super().load_custom_config()
        self.geogrid_data_path = self.custom_config["geogrid_data_path"]
        self.ungrib_data_path = self.custom_config["ungrib_data_path"]

    def __call__(self):
        WRFRUNConfig.check_wrfrun_context(error=True)

        WPS_WORK_PATH = WRFRUNConfig.WPS_WORK_PATH
        output_path = WRFRUNConfig.get_output_path()
        output_save_path = f"{output_path}/metgrid"
        log_save_path = f"{output_path}/metgrid/logs"

        # check input of metgrid.exe
        file_list = listdir(WPS_WORK_PATH)

        if "geo_em.d01.nc" not in file_list:

            if self.geogrid_data_path is None:
                self.geogrid_data_path = f"{output_path}/geogrid"
            geogrid_data_path = abspath(self.geogrid_data_path)

            if not exists(geogrid_data_path) or "geo_em.d01.nc" not in listdir(geogrid_data_path):
                logger.error(f"Can't find geogrid outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")
                raise FileNotFoundError(f"Can't find geogrid outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")

            else:
                geogrid_file_list = [x for x in listdir(geogrid_data_path) if x.startswith("geo_em.d")]
                for _file in geogrid_file_list:
                    if exists(f"{WPS_WORK_PATH}/{_file}"):
                        remove(f"{WPS_WORK_PATH}/{_file}")
                    symlink(f"{geogrid_data_path}/{_file}", f"{WPS_WORK_PATH}/{_file}")

        ungrib_output_dir = WRFRUNConfig.get_ungrib_out_dir_path()
        if basename(ungrib_output_dir) not in file_list or len(listdir(ungrib_output_dir)) == 0:

            if self.ungrib_data_path is None:
                self.ungrib_data_path = f"{output_path}/ungrib"
            ungrib_data_path = abspath(self.ungrib_data_path)

            if not exists(ungrib_data_path) or len(listdir(ungrib_data_path)) == 0:
                logger.error(f"Can't find ungrib outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")
                raise FileNotFoundError(f"Can't find ungrib outputs in WPS_WORK_PATH and your outputs directory, which is essential to run metgrid")

            else:
                ungrib_file_list = [x for x in listdir(ungrib_data_path)]
                for _file in ungrib_file_list:
                    symlink(f"{ungrib_data_path}/{_file}", f"{ungrib_output_dir}/{_file}")

        model_preprocess("metgrid", WPS_WORK_PATH)

        check_path(output_save_path, log_save_path)

        WRFRUNConfig.WRFRUN_WORK_STATUS = "metgrid"
        self.generate_custom_config()
        WRFRUNConfig.write_namelist(f"{WPS_WORK_PATH}/{NamelistName.WPS}", "wps")
        super().__call__()

        model_postprocess(WPS_WORK_PATH, log_save_path, startswith="metgrid.log", outputs="namelist.wps", copy_only=False)
        model_postprocess(WPS_WORK_PATH, output_save_path, startswith="met_em", copy_only=False, error_message="Failed to execute metgrid.exe")

        logger.info(f"All metgrid output files have been copied to {output_save_path}")


class
