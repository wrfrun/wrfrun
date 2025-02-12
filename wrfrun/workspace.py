"""
This file contains functions to interact with WRF workspace
"""

from os import symlink, listdir, makedirs
from os.path import exists
from shutil import rmtree

from .core import WRFRUNConfig, WRFRUNConstants
from .utils import logger, check_path


def prepare_workspace():
    """Initialize workspace

    """
    logger.info(f"Initialize workspace...")

    # extract WRF path
    wrf_config = WRFRUNConfig.get_wrf_config()
    wps_path = wrf_config["wps_path"]
    wrf_path = wrf_config["wrf_path"]
    wrfda_path = wrf_config["wrfda_path"]

    WRFRUN_TEMP_PATH = WRFRUNConstants.get_temp_path()
    WORK_PATH = WRFRUNConstants.get_workspace_path()
    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")
    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")
    WRFDA_WORK_PATH = WRFRUNConstants.get_work_path("wrfda")

    # check folder
    check_path(WRFRUN_TEMP_PATH)
    check_path(WRFRUNConfig.get_output_path())

    if exists(wrfda_path):
        WRFRUNConstants.USE_WRFDA = True

    # create folder to run WPS and WRF
    # check the path
    if not (exists(wps_path) and exists(wrf_path)):
        logger.error(f"Your WPS or WRF path is wrong")
        raise FileNotFoundError(f"Your WPS or WRF path is wrong")

    # remove old file
    if exists(WORK_PATH):
        logger.info(f"Remove old files...")
        rmtree(WORK_PATH)
    check_path(WPS_WORK_PATH, f"{WPS_WORK_PATH}/outputs",
               WRF_WORK_PATH, WRFDA_WORK_PATH)
    logger.info(f"Link essential files...")

    # link {wps_path}/*
    # collect file except folder geogrid
    file_list = [
        x for x in listdir(wps_path) if x not in ["geogrid", "namelist.wps"]
    ]
    for file in file_list:
        symlink(f"{wps_path}/{file}", f"{WPS_WORK_PATH}/{file}")

    # create folder geogrid and link default GEOGRID file
    makedirs(f"{WPS_WORK_PATH}/geogrid")
    symlink(
        f"{wps_path}/geogrid/GEOGRID.TBL", f"{WPS_WORK_PATH}/geogrid/GEOGRID.TBL"
    )

    # # link {wrf_path}/run/*, except namelist.input
    file_list = [x for x in listdir(
        f"{wrf_path}/run") if not x.startswith("namelist")]
    for file in file_list:
        symlink(f"{wrf_path}/run/{file}", f"{WRF_WORK_PATH}/{file}")

    if WRFRUNConstants.USE_WRFDA:
        # # link {wrfda_path}/bin/*.exe
        file_list = [x for x in listdir(f"{wrfda_path}/bin") if x.endswith(".exe")]
        for file in file_list:
            symlink(f"{wrfda_path}/bin/{file}", f"{WRFDA_WORK_PATH}/{file}")

        # # link {wrfda_path}/var/run/*
        file_list = listdir(f"{wrfda_path}/var/run")
        for file in file_list:
            symlink(f"{wrfda_path}/var/run/{file}", f"{WRFDA_WORK_PATH}/{file}")

        # # link {wrfda_path}/run/LANDUSE.TBL
        symlink(f"{wrfda_path}/run/LANDUSE.TBL", f"{WRFDA_WORK_PATH}/LANDUSE.TBL")


__all__ = ["prepare_workspace"]
