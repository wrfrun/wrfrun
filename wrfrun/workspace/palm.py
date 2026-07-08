"""
wrfrun.workspace.palm
#####################

Functions to prepare workspace for PALM model.

.. autosummary::
    :toctree: generated/

    get_palm_workspace_path
    prepare_palm_workspace
"""

from os import listdir
from os.path import abspath, exists
from pathlib import Path
from typing import Literal

from wrfrun.core import WRFRUN, WRFRUNURI
from wrfrun.log import logger
from wrfrun.utils import check_path

from .utils import create_copy

WORKSPACE_PALM = ""


def _palm_workspace_uri_hook(uri_manager: WRFRUNURI):
    """
    This function doesn't register any URI.

    This is a hook to initializes some global strings.

    :param uri_manager: ``WRFRUNURI`` instance.
    :type uri_manager: WRFRUNURI
    """
    global WORKSPACE_PALM

    WORKSPACE_PALM = f"{uri_manager.WRFRUN_WORKSPACE_MODEL}/PALM"


WRFRUN.set_uri_register_func(_palm_workspace_uri_hook)


def get_palm_workspace_path(node: Literal["root", "job", "input", "output"] = "root") -> str:
    """
    Get workspace of PALM model.

    :param node: Which dir.
    :type node: str
    :return: Workspace path.
    :rtype: str
    """
    job_name = WRFRUN.config.get_model_config("palm")["job_name"]

    match node:
        case "root":
            return WORKSPACE_PALM

        case "job":
            return f"{WORKSPACE_PALM}/job"

        case "input":
            return f"{WORKSPACE_PALM}/job/{job_name}/INPUT"

        case "output":
            return f"{WORKSPACE_PALM}/job/{job_name}/OUTPUT"


def prepare_palm_workspace(model_config: dict):
    """
    Initialize workspace for PALM model.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$HOME/.config/wrfrun/model/PALM``

    :param model_config: Model config.
    :type model_config: dict
    """
    logger.info("Initialize workspace for PALM.")

    WRFRUNConfig = WRFRUN.config

    palm_path = model_config["palm_path"]
    # config_id = model_config["config_identifier"]
    # config_file = model_config["config_file_path"]

    palm_path = abspath(palm_path)

    if not (exists(palm_path) and exists(f"{palm_path}/bin")):
        logger.error("Your PALM path is wrong.")
        raise FileNotFoundError("Your PALM path is wrong.")

    palm_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_PALM)
    job_name = WRFRUNConfig.get_model_config("palm")["job_name"]
    workspace_job_path = f"{palm_work_path}/job"
    workspace_input_path = f"{workspace_job_path}/{job_name}/INPUT"
    check_path(palm_work_path, workspace_job_path, workspace_input_path, force=True)

    if not exists(f"{palm_path}/bin/palmrun"):
        logger.error("Script 'palmrun' not found in your PALM dir.")
        raise FileNotFoundError("Script 'palmrun' not found in your PALM dir.")

    create_copy(f"{palm_path}/bin/palmrun", f"{palm_work_path}/palmrun")

    file_list = [x for x in listdir(palm_path) if not (x.startswith(".palm.config") or x == "JOBS")]
    _ = [create_copy(f"{palm_path}/{x}", f"{palm_work_path}/{x}") for x in file_list]

    # we need some tricks to hack palm runtime directory.
    # job_path = f"{palm_path}/JOBS"
    # if exists(job_path):
    #     if islink(job_path):
    #         remove(job_path)

    #     else:
    #         new_job_path = f"{job_path}_wrfrun_bak"
    #         if exists(new_job_path):
    #             rmtree(new_job_path)

    #         logger.warning(f"You have an existed PALM JOBS dir: {job_path}")
    #         logger.warning(f"wrfrun has renamed it to: {new_job_path}")
    #         logger.warning("If you have important files in it, please backup it to other positions,")
    #         logger.warning("cause wrfrun may delete the renamed depository in the future.")

    #         move(job_path, new_job_path)

    # symlink(workspace_job_path, job_path)

    # PALM config file.
    # if config_file == "":
    #     if not exists(f"{palm_path}/.palm.config.default"):
    #         logger.error(f"Can't find the default config file: '{palm_path}/.palm.config.default', please provide one.")
    #         raise FileNotFoundError(
    #             f"Can't find the default config file: '{palm_path}/.palm.config.default', please provide one."
    #         )

    #     copyfile(f"{palm_path}/.palm.config.default", f"{palm_work_path}/.palm.config.{config_id}")

    # else:
    #     symlink(abspath(config_file), f"{palm_work_path}/.palm.config.{config_id}")


def check_palm_workspace(model_config: dict) -> bool:
    """
    Check if PALM's workspace is broken.

    :param model_config: PALM's model config.
    :type model_config: dict
    :return: If check passed.
    :rtype: bool
    """
    WRFRUNConfig = WRFRUN.config

    flag = True

    palm_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_PALM)
    flag = flag & Path(palm_work_path).exists()

    return flag


__all__ = ["get_palm_workspace_path", "prepare_palm_workspace", "check_palm_workspace"]
