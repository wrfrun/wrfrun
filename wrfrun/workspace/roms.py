"""
wrfrun.workspace.roms
#####################

Functions to prepare workspace for WPS/WRF model.

.. autosummary::
    :toctree: generated/

    get_roms_workspace_path
    prepare_roms_workspace
    check_roms_workspace
"""


from wrfrun.core import WRFRUN, WRFRunConfig
from wrfrun.log import logger
from wrfrun.utils import check_path

WORKSPACE_MODEL_ROMS = ""


def _register_roms_workspace_uri(wrfrun_config: WRFRunConfig):
    """
    This function doesn't register any URI.

    This is a hook to initializes some global strings.

    :param wrfrun_config: ``WRFRUNProxy`` instance.
    :type wrfrun_config: WRFRUNProxy
    """
    global WORKSPACE_MODEL_ROMS

    WORKSPACE_MODEL_ROMS = f"{wrfrun_config.WRFRUN_WORKSPACE_MODEL}/ROMS"


WRFRUN.set_config_register_func(_register_roms_workspace_uri)


def get_roms_workspace_path() -> str:
    """
    Get workspace path of ROMS model.

    :param name: Model part name.
    :type name: str
    :return: Workspace path.
    :rtype: str
    """
    return WORKSPACE_MODEL_ROMS


def prepare_roms_workspace(model_config: dict):
    """
    Initialize workspace for ROMS model.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$HOME/.config/wrfrun/model/ROMS`

    :param model_config: Model config.
    :type model_config: dict
    """
    logger.info("Initialize workspace for ROMS.")

    WRFRUNConfig = WRFRUN.config

    roms_work_path = WRFRUNConfig.parse_resource_uri(WORKSPACE_MODEL_ROMS)
    check_path(roms_work_path, force=True)


__all__ = ["get_roms_workspace_path", "prepare_roms_workspace"]
