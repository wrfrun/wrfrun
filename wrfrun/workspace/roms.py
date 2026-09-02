"""
wrfrun.workspace.roms
#####################

Functions to prepare workspace for ROMS model.

.. autosummary::
    :toctree: generated/

    get_roms_workspace_path
    prepare_roms_workspace
"""

from wrfrun.core import WRFRUN_NEW
from wrfrun.log import logger

from ..core.type import ResourceRef


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

    roms_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_roms", ""))
    roms_work_path.mkdir(exist_ok=True, parents=True)


__all__ = ["prepare_roms_workspace"]
