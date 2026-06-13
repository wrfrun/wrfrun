"""
wrfrun.workspace.arps
#####################

Functions to prepare workspace for ARPS model and its submodels.

.. autosummary::
    :toctree: generated/

    get_palm_workspace_path
    prepare_palm_workspace
"""

from os import symlink
from os.path import abspath, exists

from wrfrun.core import WRFRUN, WRFRunConfig
from wrfrun.log import logger
from wrfrun.utils import check_path

WORKSPACE_ARPS = ""


def get_arps_workspace_path() -> str:
    """
    Get ARPS main workspace path.

    :return: ARPS main workspace.
    :rtype: str
    """
    return WORKSPACE_ARPS


def _register_arps_workspace_uri(wrfrun_config: WRFRunConfig):
    """
    This function doesn't register any URI.

    This is a hook to initializes some global strings.

    :param wrfrun_config: ``WRFRunConfig`` instance.
    :type wrfrun_config: WRFRunConfig
    """
    global WORKSPACE_ARPS

    WORKSPACE_ARPS = f"{wrfrun_config.WRFRUN_WORKSPACE_MODEL}/ARPS"


WRFRUN.set_config_register_func(_register_arps_workspace_uri)


def prepare_arps_workspace(model_config: dict):
    """
    Initialize workspace for ARPS model and its submodels.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$WORKSPACE/model/ARPS/arps``
    2. ``$WORKSPACE/model/ARPS/{SUBMODEL_NAME}``

    :param model_config: Model config.
    :type model_config: dict
    """
    logger.info("Initialize workspace for ARPS.")

    WRFRUNConfig = WRFRUN.config

    arps_bin_dir = model_config["global"]["arps_bin_directory"]
    submodel_name_list = [x for x in model_config if x not in ("use", "global", "arps")]
    arps_bin_dir = abspath(arps_bin_dir)

    if not exists(arps_bin_dir):
        logger.error("Your ARPS binary path ([magenta]arps_bin_directory[/magenta]) is wrong, check your TOML config.")
        raise FileNotFoundError("Your ARPS binary path (arps_bin_directory) is wrong, check your TOML config.")

    arps_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_ARPS)

    for _submodel in submodel_name_list:
        if not exists(f"{arps_bin_dir}/{_submodel}"):
            logger.warning(
                f"[magenta]{_submodel}[/magenta] not found in {arps_bin_dir}, mark it with [magenta]is_valid=False[/magenta]."
            )
            model_config.update({_submodel: {"is_valid": False}})

        else:
            check_path(f"{arps_work_path}/{_submodel}", force=True)
            symlink(f"{arps_bin_dir}/{_submodel}", f"{arps_work_path}/{_submodel}/{_submodel}")
            model_config.update({_submodel: {"is_valid": True}})


__all__ = ["prepare_arps_workspace", "get_arps_workspace_path"]
