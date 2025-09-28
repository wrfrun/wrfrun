"""
wrfrun.workspace
################

Prepare ``workspace`` for ``wrfrun``. For the ``workspace`` of numerical model, you should head to :doc:`model.workspace <wrfrun.model.workspace>`.

``workspace`` is a collection of several directories where ``wrfrun``, extensions and numerical model works.
These directories and their purpose are listed below.

===================================         ===========================================================
Director Path                               Purpose
===================================         ===========================================================
``/tmp/wrfrun``                             Store temporary files.
``$HOME/.config/wrfrun``                    Main work directory.
``$HOME/.config/wrfrun/replay``             Work directory for :doc:`replay <wrfrun.core.replay>`.
``$HOME/.config/wrfrun/model``              Work directory for numerical models.
===================================         ===========================================================

Inside the ``$HOME/.config/wrfrun/model``, ``wrfrun`` may create others directories depending on the model you use.
Refer to :doc:`model.workspace <wrfrun.model.workspace>` for more information.

.. autosummary::
    :toctree: generated/

    prepare_workspace
"""

from os import listdir, makedirs, symlink
from os.path import exists

from .core import WRFRUNConfig
from .utils import check_path, logger


def prepare_workspace():
    """
    Initialize ``wrfrun`` workspace.
    """
    logger.info(f"Initialize main workspace...")

    # extract WRF path
    wrf_config = WRFRUNConfig.get_model_config("wrf")
    wps_path = wrf_config["wps_path"]
    wrf_path = wrf_config["wrf_path"]
    wrfda_path = wrf_config["wrfda_path"]

    WRFRUN_TEMP_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_TEMP_PATH)
    WORK_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_ROOT)
    REPLAY_WORK_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)
    WPS_WORK_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WPS_WORK_PATH)
    WRF_WORK_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRF_WORK_PATH)
    WRFDA_WORK_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFDA_WORK_PATH)
    output_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)

    # check folder
    check_path(WRFRUN_TEMP_PATH)
    check_path(REPLAY_WORK_PATH, force=True)
    check_path(output_path)

    if exists(wrfda_path):
        WRFRUNConfig.USE_WRFDA = True

    # create folder to run WPS, and WRF
    # check the path
    if not (exists(wps_path) and exists(wrf_path)):
        logger.error(f"Your WPS or WRF path is wrong")
        raise FileNotFoundError(f"Your WPS or WRF path is wrong")

    # remove old file
    if exists(WORK_PATH):
        logger.info(f"Remove old files...")
    check_path(WPS_WORK_PATH, f"{WPS_WORK_PATH}/outputs",
               WRF_WORK_PATH, WRFDA_WORK_PATH, force=True)
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

    if WRFRUNConfig.USE_WRFDA:
        # # link {wrfda_path}/bin/*.exe
        file_list = ["da_wrfvar.exe", "da_update_bc.exe"]
        for file in file_list:
            symlink(f"{wrfda_path}/var/build/{file}", f"{WRFDA_WORK_PATH}/{file}")

        # # link {wrfda_path}/var/run/*
        file_list = listdir(f"{wrfda_path}/var/run")
        for file in file_list:
            symlink(f"{wrfda_path}/var/run/{file}", f"{WRFDA_WORK_PATH}/{file}")

        # # link {wrfda_path}/run/LANDUSE.TBL
        symlink(f"{wrfda_path}/run/LANDUSE.TBL", f"{WRFDA_WORK_PATH}/LANDUSE.TBL")


__all__ = ["prepare_workspace"]
