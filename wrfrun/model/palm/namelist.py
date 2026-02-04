"""
wrfrun.model.palm.namelist
##########################

Functions to process namelist for ``PALM``.

.. autosummary::
    :toctree: generated/

    prepare_palm_namelist
"""

from os.path import exists

from wrfrun.core import WRFRUN
from wrfrun.log import logger


def prepare_palm_namelist():
    """
    This function loads user PALM namelist file and save it in :doc:`WRFRUN </api/core.core>`.
    """
    palm_config = WRFRUN.config.get_model_config("palm")
    namelist_file = palm_config["user_namelist"]

    if not exists(namelist_file):
        logger.error(f"Can't find PALM namelist: {namelist_file}")
        raise FileNotFoundError(f"Can't find PALM namelist: {namelist_file}")

    WRFRUN.config.read_namelist(namelist_file, "palm")


__all__ = ["prepare_palm_namelist"]
