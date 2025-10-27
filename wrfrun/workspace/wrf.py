"""
wrfrun.workspace.wrf
####################

Functions to prepare workspace for WPS/WRF model.

.. autosummary::
    :toctree: generated/

    get_wrf_workspace_path
    prepare_wrf_workspace
    check_wrf_workspace
"""

from os import listdir, makedirs, symlink
from os.path import exists
from typing import Literal

from wrfrun.core import WRFRunConfig, get_wrfrun_config, set_register_func
from wrfrun.utils import check_path, logger

WORKSPACE_MODEL_WPS = ""
WORKSPACE_MODEL_WRF = ""
WORKSPACE_MODEL_WRFDA = ""


def _register_wrf_workspace_uri(wrfrun_config: WRFRunConfig):
    """
    This function doesn't register any URI.

    This is a hook to initializes some global strings.

    :param wrfrun_config: ``WRFRunConfig`` instance.
    :type wrfrun_config: WRFRunConfig
    """
    global WORKSPACE_MODEL_WPS, WORKSPACE_MODEL_WRF, WORKSPACE_MODEL_WRFDA

    WORKSPACE_MODEL_WPS = f"{wrfrun_config.WRFRUN_WORKSPACE_MODEL}/WPS"
    WORKSPACE_MODEL_WRF = f"{wrfrun_config.WRFRUN_WORKSPACE_MODEL}/WRF"
    WORKSPACE_MODEL_WRFDA = f"{wrfrun_config.WRFRUN_WORKSPACE_MODEL}/WRFDA"


set_register_func(_register_wrf_workspace_uri)


def get_wrf_workspace_path(name: Literal["wps", "wrf", "wrfda"]) -> str:
    """
    Get workspace path of WRF model.

    :param name: Model part name.
    :type name: str
    :return: Workspace path.
    :rtype: str
    """
    match name:
        case "wps":
            return WORKSPACE_MODEL_WPS

        case "wrf":
            return WORKSPACE_MODEL_WRF

        case "wrfda":
            return WORKSPACE_MODEL_WRFDA


def prepare_wrf_workspace(model_config: dict):
    """
    Initialize workspace for WPS/WRF model.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$HOME/.config/wrfrun/model/WPS``
    2. ``$HOME/.config/wrfrun/model/WRF``
    3. ``$HOME/.config/wrfrun/model/WRFDA``

    :param model_config: Model config.
    :type model_config: dict
    """
    logger.info(f"Initialize workspace for WPS/WRF.")

    WRFRUNConfig = get_wrfrun_config()

    wps_path = model_config["wps_path"]
    wrf_path = model_config["wrf_path"]
    wrfda_path = model_config["wrfda_path"]

    if not (wps_path and wrf_path):
        logger.warning(f"No WPS/WRF model installation path given, skip initialization.")
        return

    if wps_path:
        if not exists(wps_path):
            logger.error(f"Your WPS path is wrong.")
            raise FileNotFoundError(f"Your WPS path is wrong.")

        wps_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WPS)
        check_path(wps_work_path, f"{wps_work_path}/outputs", force=True)

        file_list = [x for x in listdir(wps_path) if x not in ["geogrid", "namelist.wps"]]
        _ = [symlink(f"{wps_path}/{file}", f"{wps_work_path}/{file}") for file in file_list]
        makedirs(f"{wps_work_path}/geogrid")
        symlink(f"{wps_path}/geogrid/GEOGRID.TBL", f"{wps_work_path}/geogrid/GEOGRID.TBL")

    if wrf_path:
        if not exists(wrf_path):
            logger.error(f"Your WRF path is wrong.")
            raise FileNotFoundError(f"Your WRF path is wrong.")

        wrf_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WRF)
        check_path(wrf_work_path, force=True)

        file_list = [x for x in listdir(f"{wrf_path}/run") if not x.startswith("namelist")]
        _ = [symlink(f"{wrf_path}/run/{file}", f"{wrf_work_path}/{file}") for file in file_list]

    if wrfda_path:
        if not exists(wrfda_path):
            logger.error(f"Your WRFDA path is wrong.")
            raise FileNotFoundError(f"Your WRFDA path is wrong.")

        wrfda_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WRFDA)
        check_path(wrfda_work_path, force=True)

        file_list = ["da_wrfvar.exe", "da_update_bc.exe"]
        _ = [symlink(f"{wrfda_path}/var/build/{file}", f"{wrfda_work_path}/{file}") for file in file_list]

        file_list = listdir(f"{wrfda_path}/var/run")
        _ = [symlink(f"{wrfda_path}/var/run/{file}", f"{wrfda_work_path}/{file}") for file in file_list]

        symlink(f"{wrfda_path}/run/LANDUSE.TBL", f"{wrfda_work_path}/LANDUSE.TBL")


def check_wrf_workspace(model_config: dict) -> bool:
    """
    Check if WPS/WRF workspace exists.

    :param model_config: Model config.
    :type model_config: dict
    :return: ``True`` if WPS/WRF workspace exists, ``False`` otherwise.
    :rtype: bool
    """
    WRFRUNConfig = get_wrfrun_config()

    wps_path = model_config["wps_path"]
    wrf_path = model_config["wrf_path"]
    wrfda_path = model_config["wrfda_path"]

    flag = True

    if wps_path:
        wps_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WPS)
        flag = flag & exists(wps_work_path)

    if wrf_path:
        wrf_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WRF)
        flag = flag & exists(wrf_work_path)

    if wrfda_path:
        wrfda_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_WRFDA)
        flag = flag & exists(wrfda_work_path)

    return flag


__all__ = ["get_wrf_workspace_path", "prepare_wrf_workspace", "check_wrf_workspace"]
