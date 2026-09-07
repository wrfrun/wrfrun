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

from os.path import dirname, exists
from shutil import move, rmtree
from typing import Callable, Literal

from wrfrun.core import WRFRUN_NEW
from wrfrun.log import check_path, logger

from .arps import check_arps_workspace, prepare_arps_workspace
from .palm import check_palm_workspace, prepare_palm_workspace
from .roms import prepare_roms_workspace
from .wrf import check_wrf_workspace, prepare_wrf_workspace

PREPARE_FUNC_MAP = {
    "arps": prepare_arps_workspace,
    "wrf": prepare_wrf_workspace,
    "palm": prepare_palm_workspace,
    "roms": prepare_roms_workspace,
}
CHECK_FUNC_MAP = {"arps": check_arps_workspace, "wrf": check_wrf_workspace, "palm": check_palm_workspace}


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

    workspace_backup_path = None
    initialize_success = False

    wrfrun_temp_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.TEMP_DIR)
    workspace_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.WORKSPACE_DIR)
    replay_work_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.OUTPUT_DIR)

    if exists(workspace_path):
        logger.info(f"Reinitialize main workspace at: '{workspace_path}'")
        # backup old workspace, so we can restore it if we failed to create new workspace.
        workspace_backup_path = f"{dirname(workspace_path)}/.workspace_backup"
        move(workspace_path, workspace_backup_path)

    else:
        logger.info(f"Initialize main workspace at: '{workspace_path}'")

    # check folder
    check_path(wrfrun_temp_path)
    check_path(replay_work_path)
    check_path(output_path)

    model_configs = WRFRUN_NEW.config["model"]

    try:
        for model_name in model_configs:
            if model_name not in PREPARE_FUNC_MAP:
                logger.warning(f"Function to prepare '{model_name}' workspace not found, workspace may be incomplete")
                continue

            PREPARE_FUNC_MAP[model_name](model_configs[model_name])

        initialize_success = True

    finally:
        if initialize_success and workspace_backup_path:
            rmtree(workspace_backup_path)

        else:
            logger.warning("Failed to initialize workspace.")

            if workspace_backup_path:
                rmtree(workspace_path)
                move(workspace_backup_path, workspace_path)
                logger.warning("Old workspace restored.")


def check_workspace() -> bool:
    """
    Check if workspace exists.

    :return: ``True`` if workspace exists, ``False`` otherwise.
    :rtype: bool
    """
    global CHECK_FUNC_MAP

    wrfrun_temp_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.TEMP_DIR)
    workspace_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.WORKSPACE_DIR)
    replay_work_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.WRFRUN_WORKSPACE_REPLAY)
    output_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.OUTPUT_DIR)

    flag = True
    flag = flag & exists(wrfrun_temp_path) & exists(replay_work_path) & exists(output_path) & exists(workspace_path)

    model_configs = WRFRUN_NEW.config["model"]

    for model_name in model_configs:
        if model_name == "debug_level":
            continue

        if model_name not in CHECK_FUNC_MAP:
            logger.info(f"Function to check '{model_name}' workspace not found, skip")
            continue

        flag = flag & CHECK_FUNC_MAP[model_name](model_configs[model_name])

    return flag


__all__ = ["prepare_workspace", "check_workspace"]
