"""
wrfrun.model.palm.workspace
###########################

Prepare and validate PALM workspaces.

.. autosummary::
    :toctree: generated/

    get_palm_workspace_path
    prepare_palm_workspace
    check_palm_workspace
"""

from os import listdir
from pathlib import Path
from typing import Literal

from wrfrun.core import WRFRUN, ResourceRef
from wrfrun.log import logger


def get_palm_workspace_path(node: Literal["root", "job", "input", "output"] = "root") -> ResourceRef:
    """
    Get workspace of PALM model.

    :param node: Which dir.
    :type node: str
    :return: Workspace path.
    :rtype: ResourceRef
    """
    job_name = WRFRUN.config.get_model_config("palm")["job_name"]

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
    """Stage PALM runtime files in the model-owned workspace."""
    logger.info("Initialize workspace for PALM.")

    palm_path = WRFRUN.config.get_model_config("palm")["palm_path"]

    palm_path = Path(palm_path).resolve()

    if not (palm_path / "bin").is_dir():
        logger.error(f"Your PALM path is wrong: {palm_path}")
        raise FileNotFoundError(f"Your PALM path is wrong: {palm_path}")

    palm_work_path = get_palm_workspace_path()
    workspace_job_path = get_palm_workspace_path("job")
    workspace_input_path = get_palm_workspace_path("input")
    WRFRUN.resource.mkdir(palm_work_path)
    WRFRUN.resource.mkdir(workspace_job_path)
    WRFRUN.resource.mkdir(workspace_input_path)

    if not (palm_path / "bin/palmrun").is_file():
        logger.error("Script 'palmrun' not found in your PALM dir.")
        raise FileNotFoundError("Script 'palmrun' not found in your PALM dir.")

    WRFRUN.io.symlink(file_path=palm_path / "bin/palmrun", save_path=palm_work_path / "palmrun")

    file_list = [x for x in listdir(palm_path) if not (x.startswith(".palm.config") or x == "JOBS")]
    _ = [WRFRUN.io.symlink(file_path=f"{palm_path}/{x}", save_path=palm_work_path / x) for x in file_list]


def check_palm_workspace() -> bool:
    """
    Check if PALM's workspace is broken.

    :return: If check passed.
    :rtype: bool
    """
    flag = True

    palm_work_path = get_palm_workspace_path()
    flag = flag & WRFRUN.resource.get_custom_resource(palm_work_path).exists()

    return flag


__all__ = ["get_palm_workspace_path", "prepare_palm_workspace", "check_palm_workspace"]
