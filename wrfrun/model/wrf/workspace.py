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

from os import listdir
from pathlib import Path

from wrfrun.core import WRFRUN_NEW
from wrfrun.core.type import ResourceRef
from wrfrun.log import logger


def prepare_wrf_workspace():
    """
    Initialize workspace for WPS/WRF model.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$HOME/.config/wrfrun/model/WPS``
    2. ``$HOME/.config/wrfrun/model/WRF``
    3. ``$HOME/.config/wrfrun/model/WRFDA``
    """
    logger.info("Initialize workspace for WPS/WRF.")

    model_config = WRFRUN_NEW.config.get_model_config(model_name="wrf")

    wps_path = Path(model_config["wps_path"])
    wrf_path = Path(model_config["wrf_path"])
    wrfda_path = Path(model_config["wrfda_path"])

    if wps_path.is_dir():
        wps_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wps"))
        (wps_work_path / "outputs").mkdir(exist_ok=True, parents=True)
        (wps_work_path / "geogrid").mkdir(exist_ok=True)

        file_list = [x for x in listdir(wps_path) if x not in ["geogrid", "namelist.wps"]]
        for file in file_list:
            WRFRUN_NEW.io.symlink(
                file_path=wps_path / file,
                save_path=wps_work_path / file,
            )
        WRFRUN_NEW.io.copy(
            file_path=wps_path / "geogrid/GEOGRID.TBL",
            save_path=wps_work_path / "geogrid/GEOGRID.TBL",
        )

    else:
        logger.warning("Skip init WPS workspace because its path is invalid.")

    if wrf_path.is_dir():
        wrf_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wrf"))
        wrf_work_path.mkdir(exist_ok=True, parents=True)

        file_list = [x for x in listdir(f"{wrf_path}/run") if not x.startswith("namelist")]
        for file in file_list:
            WRFRUN_NEW.io.symlink(
                file_path=wrf_path / "run" / file,
                save_path=wrf_work_path / file,
            )

    else:
        logger.warning("Skip init WRF workspace because its path is invalid.")

    if wrfda_path.is_dir():
        wrfda_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_wrf", "wrfda"))
        wrfda_work_path.mkdir(exist_ok=True, parents=True)

        file_list = ["da_wrfvar.exe", "da_update_bc.exe"]
        for file in file_list:
            WRFRUN_NEW.io.copy(
                file_path=wrfda_path / "var/build" / file,
                save_path=wrfda_work_path / file,
            )

        file_list = listdir(f"{wrfda_path}/var/run")
        for file in file_list:
            WRFRUN_NEW.io.symlink(
                file_path=wrfda_path / "var/run" / file,
                save_path=wrfda_work_path / file,
            )

        WRFRUN_NEW.io.copy(
            file_path=wrfda_path / "run/LANDUSE.TBL",
            save_path=wrfda_work_path / "LANDUSE.TBL",
        )

    else:
        logger.warning("Skip init WRFDA workspace because its path is invalid.")


def check_wrf_workspace() -> bool:
    """
    Check if WPS/WRF workspace exists.

    :return: ``True`` if WPS/WRF workspace exists, ``False`` otherwise.
    :rtype: bool
    """
    model_config = WRFRUN_NEW.config.get_model_config("wrf")

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
