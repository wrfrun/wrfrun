"""
wrfrun.workspace.core
#####################

Core functions to prepare ``wrfrun`` workspace.

.. autosummary::
    :toctree: generated/

    prepare_workspace
"""

from os.path import exists
from shutil import rmtree

from wrfrun import WRFRUNConfig
from wrfrun.utils import check_path, logger
from .wrf import prepare_wrf_workspace


def prepare_workspace():
    """
    Initialize ``wrfrun`` workspace.

    This function will check following paths,
    and create them if them don't exist:

    1. ``/tmp/wrfrun``
    2. ``$HOME/.config/wrfrun``
    3. ``$HOME/.config/wrfrun/replay``
    4. ``$HOME/.config/wrfrun/model``

    It will call other responding functions to initialize workspace for numerical models:

    1. :doc:`WPS/WRF model </api/workspace.wrf>`
    """
    logger.info(f"Initialize main workspace...")

    WRFRUN_TEMP_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_TEMP_PATH)
    workspace_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_ROOT)
    REPLAY_WORK_PATH = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)

    if exists(workspace_path):
        logger.info(f"Remove old files in workspace.")
        rmtree(workspace_path)

    # check folder
    check_path(WRFRUN_TEMP_PATH)
    check_path(REPLAY_WORK_PATH)
    check_path(output_path)

    func_map = {
        "wrf": prepare_wrf_workspace
    }
    model_configs = WRFRUNConfig["model"]

    for model_name in model_configs:
        func_map[model_name](model_configs[model_name])


__all__ = ["prepare_workspace"]
