"""
wrfrun.workspace.arps
#####################

Functions to prepare workspace for ARPS model and its submodels.

.. autosummary::
    :toctree: generated/

    get_arps_workspace_path
    prepare_arps_workspace
"""

from os import symlink
from os.path import abspath, exists

from wrfrun.core import WRFRUN, WRFRUNURI
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


def _arps_workspace_uri_hook(uri_manager: WRFRUNURI):
    """
    This function doesn't register any URI.

    This is a hook to initializes some global strings.

    :param uri_manager: ``WRFRUNURI`` instance.
    :type uri_manager: WRFRUNURI
    """
    global WORKSPACE_ARPS

    WORKSPACE_ARPS = f"{uri_manager.WRFRUN_WORKSPACE_MODEL}/ARPS"


WRFRUN.set_uri_register_func(_arps_workspace_uri_hook)


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

    # arps core has two version: arps and arps_mpi, we also need to check arps_mpi
    if not exists(f"{arps_bin_dir}/arps_mpi"):
        logger.warning(
            f"[magenta]arps_mpi[/magenta] not found in {arps_bin_dir}. "
            "If you want to run arps with MPI, make sure you have compiled MPI version of ARPS core."
        )
        model_config.update({"arps_mpi": {"is_valid": False}})
    else:
        check_path(f"{arps_work_path}/arps_mpi", force=True)
        symlink(f"{arps_bin_dir}/arps_mpi", f"{arps_work_path}/arps_mpi/arps_mpi")
        model_config.update({"arps_mpi": {"is_valid": True}})


__all__ = ["prepare_arps_workspace", "get_arps_workspace_path"]
