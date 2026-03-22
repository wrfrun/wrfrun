"""
wrfrun.workspace.core
#####################

Core functions to prepare ``wrfrun`` workspace.

.. autosummary::
    :toctree: generated/

    register_workspace_func
    prepare_workspace
    check_workspace
"""

from os.path import exists
from shutil import rmtree
from typing import Callable, Literal

from wrfrun.core import WRFRUN
from wrfrun.log import check_path, logger

from .palm import prepare_palm_workspace
from .wrf import check_wrf_workspace, prepare_wrf_workspace

PREPARE_FUNC_MAP = {"wrf": prepare_wrf_workspace, "palm": prepare_palm_workspace}
CHECK_FUNC_MAP = {"wrf": check_wrf_workspace}


def register_workspace_func(model_name: str, func: Callable[[dict], bool], func_type: Literal["prepare", "check"]) -> bool:
    """
    Register a workspace function for a model.

    :param model_name: _description_
    :type model_name: str
    :param func: Workspace process function.
    :type func: Callable[[dict], bool]
    :param func_type: Type of the function.
    :type func_type: Literal["prepare", "check"]
    :return: If successfully register.
    :rtype: bool
    """
    global PREPARE_FUNC_MAP, CHECK_FUNC_MAP

    flag = False

    if func_type == "prepare":
        if model_name not in PREPARE_FUNC_MAP:
            PREPARE_FUNC_MAP[model_name] = func
            flag = True

    elif func_type == "check":
        if model_name not in CHECK_FUNC_MAP:
            CHECK_FUNC_MAP[model_name] = func
            flag = True

    else:
        logger.error(f"Unknown function type: {func_type}")
        raise ValueError(f"Unknown function type: {func_type}")

    return flag


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
    global PREPARE_FUNC_MAP

    WRFRUNConfig = WRFRUN.config

    wrfrun_temp_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_TEMP_PATH)
    workspace_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_ROOT)
    replay_work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)

    logger.info(f"Initialize main workspace at: '{workspace_path}'")

    if exists(workspace_path):
        logger.info("Remove old files in workspace.")
        rmtree(workspace_path)

    # check folder
    check_path(wrfrun_temp_path)
    check_path(replay_work_path)
    check_path(output_path)

    model_configs = WRFRUNConfig["model"]

    for model_name in model_configs:
        if model_name not in PREPARE_FUNC_MAP:
            logger.warning(f"Function to prepare '{model_name}' workspace not found, workspace may be incomplete")
            continue

        PREPARE_FUNC_MAP[model_name](model_configs[model_name])


def check_workspace() -> bool:
    """
    Check if workspace exists.

    :return: ``True`` if workspace exists, ``False`` otherwise.
    :rtype: bool
    """
    global CHECK_FUNC_MAP

    WRFRUNConfig = WRFRUN.config

    wrfrun_temp_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_TEMP_PATH)
    workspace_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_ROOT)
    replay_work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)

    flag = True
    flag = flag & exists(wrfrun_temp_path) & exists(replay_work_path) & exists(output_path) & exists(workspace_path)

    model_configs = WRFRUNConfig["model"]

    for model_name in model_configs:
        if model_name == "debug_level":
            continue

        if model_name not in CHECK_FUNC_MAP:
            logger.info(f"Function to check '{model_name}' workspace not found, skip")
            continue

        flag = flag & CHECK_FUNC_MAP[model_name](model_configs[model_name])

    return True


__all__ = ["prepare_workspace", "check_workspace"]
