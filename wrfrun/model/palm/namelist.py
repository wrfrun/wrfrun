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


def get_namelist_save_name() -> str:
    """
    Get the save name of namelist file.

    :raises KeyError: Unknown simulation type set in config file.
    :return: Save name.
    :rtype: str
    """
    map_dict = {"d3#": "_p3d", "d3r": "_p3dr", "pcr": "_pcr"}

    config = WRFRUN.config.get_model_config("palm")
    simulation_type = config["simulation_type"]
    job_name = config["job_name"]

    if simulation_type in map_dict:
        return f"{job_name}{map_dict[simulation_type]}"

    logger.error(f"Unknown simulation type: Expect {tuple(map_dict.keys())}")
    raise KeyError(f"Unknown simulation type: Expect {tuple(map_dict.keys())}")


__all__ = ["prepare_palm_namelist", "get_namelist_save_name"]
