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
from pathlib import Path
from typing import Literal

from wrfrun.core import WRFRUN_NEW, ResourceRef
from wrfrun.log import logger


def get_palm_workspace_path(node: Literal["root", "job", "input", "output"] = "root") -> ResourceRef:
    """
    Get workspace of PALM model.

    :param node: Which dir.
    :type node: str
    :return: Workspace path.
    :rtype: str
    """
    job_name = WRFRUN_NEW.config.get_model_config("palm")["job_name"]

    match node:
        case "root":
            return ResourceRef("workspace_palm", "")

        case "job":
            return ResourceRef("workspace_palm", "") / "job"

        case "input":
            return ResourceRef("workspace_palm", "") / f"job/{job_name}/INPUT"

        case "output":
            return ResourceRef("workspace_palm", "") / f"job/{job_name}/OUTPUT"


def prepare_palm_workspace():
    """
    Initialize workspace for PALM model.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$HOME/.config/wrfrun/model/PALM``
    """
    logger.info("Initialize workspace for PALM.")

    palm_path = WRFRUN_NEW.config.get_model_config("palm")["palm_path"]

    palm_path = Path(palm_path).resolve()

    if not (palm_path / "bin").is_dir():
        logger.error(f"Your PALM path is wrong: {palm_path}")
        raise FileNotFoundError(f"Your PALM path is wrong: {palm_path}")

    palm_work_path = get_palm_workspace_path()
    workspace_job_path = get_palm_workspace_path("job")
    workspace_input_path = get_palm_workspace_path("input")
    WRFRUN_NEW.resource.mkdir(palm_work_path)
    WRFRUN_NEW.resource.mkdir(workspace_job_path)
    WRFRUN_NEW.resource.mkdir(workspace_input_path)

    if not (palm_path / "bin/palmrun").is_file():
        logger.error("Script 'palmrun' not found in your PALM dir.")
        raise FileNotFoundError("Script 'palmrun' not found in your PALM dir.")

    WRFRUN_NEW.io.symlink(file_path=palm_path / "bin/palmrun", save_path=palm_work_path / "palmrun")

    file_list = [x for x in listdir(palm_path) if not (x.startswith(".palm.config") or x == "JOBS")]
    _ = [WRFRUN_NEW.io.symlink(file_path=f"{palm_path}/{x}", save_path=palm_work_path / x) for x in file_list]


def check_palm_workspace() -> bool:
    """
    Check if PALM's workspace is broken.

    :return: If check passed.
    :rtype: bool
    """
    flag = True

    palm_work_path = get_palm_workspace_path()
    flag = flag & WRFRUN_NEW.resource.get_custom_resource(palm_work_path).exists()

    return flag


__all__ = ["get_palm_workspace_path", "prepare_palm_workspace", "check_palm_workspace"]
