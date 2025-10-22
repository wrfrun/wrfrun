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
from .wrf import prepare_wrf_workspace, check_wrf_workspace


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
    logger.info(f"Initialize main workspace.")

    wrfrun_temp_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_TEMP_PATH)
    workspace_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_ROOT)
    replay_work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)

    if exists(workspace_path):
        logger.info(f"Remove old files in workspace.")
        rmtree(workspace_path)

    # check folder
    check_path(wrfrun_temp_path)
    check_path(replay_work_path)
    check_path(output_path)

    func_map = {
        "wrf": prepare_wrf_workspace
    }
    model_configs = WRFRUNConfig["model"]

    for model_name in model_configs:
        func_map[model_name](model_configs[model_name])


def check_workspace() -> bool:
    """
    Check if workspace exists.

    :return: ``True`` if workspace exists, ``False`` otherwise.
    :rtype: bool
    """

    wrfrun_temp_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_TEMP_PATH)
    workspace_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_ROOT)
    replay_work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)

    flag = True
    flag = flag & exists(wrfrun_temp_path) & exists(replay_work_path) & exists(output_path) & exists(workspace_path)

    func_map = {
        "wrf": check_wrf_workspace
    }
    model_configs = WRFRUNConfig["model"]

    for model_name in model_configs:
        if model_name == "debug_level":
            continue

        flag = flag & func_map[model_name](model_configs[model_name])

    return True


__all__ = ["prepare_workspace", "check_workspace"]
