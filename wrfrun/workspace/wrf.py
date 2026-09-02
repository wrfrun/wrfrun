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

from os import listdir, symlink
from os.path import exists

from wrfrun.core import WRFRUN_NEW
from wrfrun.log import logger

from ..core.type import ResourceRef
from .utils import create_copy


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
    logger.info("Initialize workspace for WPS/WRF.")

    wps_path = model_config["wps_path"]
    wrf_path = model_config["wrf_path"]
    wrfda_path = model_config["wrfda_path"]

    if not (wps_path and wrf_path):
        logger.error("WPS/WRF model installation path isn't set in config file.")
        raise ValueError("WPS/WRF model installation path isn't set in config file.")

    if wps_path:
        if not exists(wps_path):
            logger.error("Your WPS path is wrong.")
            raise FileNotFoundError("Your WPS path is wrong.")

        wps_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wps"))
        (wps_work_path / "outputs").mkdir(exist_ok=True, parents=True)
        (wps_work_path / "geogrid").mkdir(exist_ok=True)

        file_list = [x for x in listdir(wps_path) if x not in ["geogrid", "namelist.wps"]]
        _ = [symlink(f"{wps_path}/{file}", wps_work_path / file) for file in file_list]
        create_copy(f"{wps_path}/geogrid/GEOGRID.TBL", wps_work_path / "geogrid/GEOGRID.TBL")

    if wrf_path:
        if not exists(wrf_path):
            logger.error("Your WRF path is wrong.")
            raise FileNotFoundError("Your WRF path is wrong.")

        wrf_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wrf"))
        wrf_work_path.mkdir(exist_ok=True, parents=True)

        file_list = [x for x in listdir(f"{wrf_path}/run") if not x.startswith("namelist")]
        _ = [symlink(f"{wrf_path}/run/{file}", wrf_work_path / file) for file in file_list]

    if wrfda_path:
        if not exists(wrfda_path):
            logger.error("Your WRFDA path is wrong.")
            raise FileNotFoundError("Your WRFDA path is wrong.")

        wrfda_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wrfda"))
        wrfda_work_path.mkdir(exist_ok=True, parents=True)

        file_list = ["da_wrfvar.exe", "da_update_bc.exe"]
        _ = [create_copy(f"{wrfda_path}/var/build/{file}", wrfda_work_path / file) for file in file_list]

        file_list = listdir(f"{wrfda_path}/var/run")
        _ = [symlink(f"{wrfda_path}/var/run/{file}", wrfda_work_path / file) for file in file_list]

        create_copy(f"{wrfda_path}/run/LANDUSE.TBL", wrfda_work_path / "LANDUSE.TBL")


def check_wrf_workspace(model_config: dict) -> bool:
    """
    Check if WPS/WRF workspace exists.

    :param model_config: Model config.
    :type model_config: dict
    :return: ``True`` if WPS/WRF workspace exists, ``False`` otherwise.
    :rtype: bool
    """
    wps_path = model_config["wps_path"]
    wrf_path = model_config["wrf_path"]
    wrfda_path = model_config["wrfda_path"]

    flag = True

    if wps_path:
        wps_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wps"))
        flag = flag & wps_work_path.is_dir()

    if wrf_path:
        wrf_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wrf"))
        flag = flag & wrf_work_path.is_dir()

    if wrfda_path:
        wrfda_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wrfda"))
        flag = flag & wrfda_work_path.is_dir()

    return flag


__all__ = ["prepare_wrf_workspace", "check_wrf_workspace"]
