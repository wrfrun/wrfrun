"""
wrfrun.model.wrf.plot
#####################

Functions to generate config to plot domain area.

.. autosummary::
    :toctree: generated/

    domain_settings_from_config_wrf
    domain_settings_from_namelist_wrf
"""

from os.path import exists
from typing import Union

import f90nml

from wrfrun.core import WRFRUN
from wrfrun.log import logger

from ..type import DomainSetting


def domain_settings_from_config_wrf() -> DomainSetting:
    """
    Generate domain settings based on the config from :doc:`WRFRUN </api/core.core>`.

    :return: :class:`DomainSetting <wrfrun.model.type.DomainSetting>` object.
    :rtype: DomainSetting
    """
    user_settings = WRFRUN.config.get_model_config("wrf")["domain"]
    domain_settings: DomainSetting = {
        "resolution_x": user_settings["dx"],
        "resolution_y": user_settings["dy"],
        "points_y": user_settings["e_sn"],
        "points_x": user_settings["e_we"],
        "x_parent_index": user_settings["i_parent_start"],
        "y_parent_index": user_settings["j_parent_start"],
        "domain_num": user_settings["domain_num"],
        "grid_spacing_ratio": user_settings["parent_grid_ratio"],
        "reference_lat": user_settings["ref_lat"],
        "reference_lon": user_settings["ref_lon"],
        "true_lat1": user_settings["truelat1"],
        "true_lat2": user_settings["truelat2"],
        "stand_lon": user_settings["stand_lon"],
        "projection_type": user_settings["map_proj"],
    }

    return domain_settings


def domain_settings_from_namelist_wrf(namelist: Union[str, dict]) -> DomainSetting:
    """
    Read values from WPS/WRF namelist and generate domain settings.

    You can give either the path of namelist file or the dict returned by ``f90nml``.

    1. Parse values in a namelist file.

    >>> namelist_file_path = "./namelist.wps"
    >>> domain_settings = domain_settings_from_namelist_wrf(namelist_file_path)

    2. Parse values from dict.

    >>> namelist_file_path = "./namelist.wps"
    >>> namelist_data = f90nml.read(namelist_file_path).todict()
    >>> domain_settings = domain_settings_from_namelist_wrf(namelist_data)

    :param namelist: Path of the namelist file or the dict returned by ``f90nml``.
    :type namelist: str | dict
    :return: :class:`DomainSetting <wrfrun.model.type.DomainSetting>`.
    :rtype: DomainSetting
    """
    if isinstance(namelist, str):
        if not exists(namelist):
            logger.error(f"Namelist file not found: {namelist}")
            raise FileNotFoundError(namelist)

        namelist = f90nml.read(namelist).todict()

    domain_setting: DomainSetting = {
        "resolution_x": namelist["geogrid"]["dx"],
        "resolution_y": namelist["geogrid"]["dy"],
        "points_y": namelist["geogrid"]["e_sn"],
        "points_x": namelist["geogrid"]["e_we"],
        "x_parent_index": namelist["geogrid"]["i_parent_start"],
        "y_parent_index": namelist["geogrid"]["j_parent_start"],
        "domain_num": namelist["share"]["max_dom"],
        "grid_spacing_ratio": namelist["geogrid"]["parent_grid_ratio"],
        "reference_lat": namelist["geogrid"]["ref_lat"],
        "reference_lon": namelist["geogrid"]["ref_lon"],
        "true_lat1": namelist["geogrid"]["truelat1"],
        "true_lat2": namelist["geogrid"]["truelat2"],
        "stand_lon": namelist["geogrid"]["stand_lon"],
        "projection_type": namelist["geogrid"]["map_proj"],
    }

    return domain_setting


__all__ = ["domain_settings_from_config_wrf", "domain_settings_from_namelist_wrf"]
