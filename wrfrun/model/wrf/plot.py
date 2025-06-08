import logging
from os.path import exists
from typing import Literal, Optional, TypedDict, Union

import f90nml
from cartopy import crs

from wrfrun import WRFRUNConfig


logger = logging.getLogger("wrfrun")


class DomainSetting(TypedDict):
    """
    Domain settings which can be used to create a projection.
    """
    dx: int
    dy: int
    e_sn: Union[list[int], tuple[int]]
    e_we: Union[list[int], tuple[int]]
    i_parent_start: Union[list[int], tuple[int]]
    j_parent_start: Union[list[int], tuple[int]]
    max_dom: int
    parent_grid_ratio: Union[list[int], tuple[int]]
    map_proj: Literal["lambert", "polar", "mercator", "lat-lon"]
    ref_lat: Union[int, float]
    ref_lon: Union[int, float]
    truelat1: Union[int, float]
    truelat2: Union[int, float]
    stand_lon: Union[int, float]


def create_projection(domain_settings: Optional[DomainSetting] = None) -> crs.Projection:
    """
    Create a projection from domain settings which can be used to draw images.

    You can give your custom domain settings to create the projection.
    Please see ``wrfrun.mode.plot.DomainSetting`` for more information about ``domain_settings``.

    :return: Projection object.
    :rtype: Projection
    """
    if domain_settings is None:
        user_settings = WRFRUNConfig.get_model_config("wrf")["domain"]
        domain_settings: DomainSetting = {
            "dx": user_settings["dx"],
            "dy": user_settings["dy"],
            "e_sn": user_settings["e_sn"],
            "e_we": user_settings["e_we"],
            "i_parent_start": user_settings["i_parent_start"],
            "j_parent_start": user_settings["j_parent_start"],
            "max_dom": user_settings["domain_num"],
            "parent_grid_ratio": user_settings["parent_grid_ratio"],
            "ref_lat": user_settings["ref_lat"],
            "ref_lon": user_settings["ref_lon"],
            "truelat1": user_settings["truelat1"],
            "truelat2": user_settings["truelat2"],
            "stand_lon": user_settings["stand_lon"],
            "map_proj": user_settings["map_proj"]["name"]
        }

    match domain_settings["map_proj"]:

        case "lat-lon":
            proj = crs.PlateCarree(central_longitude=domain_settings["ref_lon"])

        case "lambert":
            false_easting = (domain_settings["e_we"][0] - 1) / 2 * domain_settings["dx"]
            false_northing = (domain_settings["e_sn"][0] - 1) / 2 * domain_settings["dy"]
            proj = crs.LambertConformal(
                central_longitude=domain_settings["ref_lon"],
                central_latitude=domain_settings["ref_lat"],
                standard_parallels=(
                    domain_settings["truelat1"],
                    domain_settings["truelat2"]
                ),
                false_easting=false_easting,
                false_northing=false_northing
            )

        case "polar":
            ref_lat = domain_settings["ref_lat"]
            if ref_lat > 0:
                proj = crs.NorthPolarStereo(central_longitude=domain_settings["stand_lon"])

            else:
                proj = crs.SouthPolarStereo(central_longitude=domain_settings["stand_lon"])

        case "mercator":
            false_easting = (domain_settings["e_we"][0] - 1) / 2 * domain_settings["dx"]
            false_northing = (domain_settings["e_sn"][0] - 1) / 2 * domain_settings["dy"]
            proj = crs.Mercator(
                central_longitude=domain_settings["ref_lon"],
                min_latitude=domain_settings["truelat1"],
                max_latitude=domain_settings["truelat2"],
                latitude_true_scale=domain_settings["stand_lon"],
                false_northing=false_northing,
                false_easting=false_easting
            )

        case _:
            logger.error(f"Unknown projection name: {domain_settings['map_proj']}")
            raise KeyError(f"Unknown projection name: {domain_settings['map_proj']}")

    return proj


def parse_domain_setting(namelist: Union[str, dict]) -> DomainSetting:
    """
    Read values from namelist and return typed dict ``DomainSetting``.

    You can give either the path of namelist file or the dict returned by ``f90nml``.

    1. Parse values in a namelist file.

    >>> namelist_file_path = "./namelist.wps"
    >>> domain_setting = parse_domain_setting(namelist_file_path)

    2. Parse values from dict.

    >>> namelist_file_path = "./namelist.wps"
    >>> namelist_data = f90nml.read(namelist_file_path).todict()
    >>> domain_setting = parse_domain_setting(namelist_data)

    :param namelist: Path of the namelist file or the dict returned by ``f90nml``.
    :type namelist: str | dict
    :return: ``DomainSetting`` dict.
    :rtype: DomainSetting
    """
    if isinstance(namelist, str):
        if not exists(namelist):
            logger.error(f"Namelist file not found: {namelist}")
            raise FileNotFoundError(namelist)

        namelist = f90nml.read(namelist).todict()

    domain_setting: DomainSetting = {
        "dx": namelist["geogrid"]["dx"],
        "dy": namelist["geogrid"]["dy"],
        "e_sn": namelist["geogrid"]["e_sn"],
        "e_we": namelist["geogrid"]["e_we"],
        "i_parent_start": namelist["geogrid"]["i_parent_start"],
        "j_parent_start": namelist["geogrid"]["j_parent_start"],
        "max_dom": namelist["share"]["max_dom"],
        "parent_grid_ratio": namelist["geogrid"]["parent_grid_ratio"],
        "ref_lat": namelist["geogrid"]["ref_lat"],
        "ref_lon": namelist["geogrid"]["ref_lon"],
        "truelat1": namelist["geogrid"]["truelat1"],
        "truelat2": namelist["geogrid"]["truelat2"],
        "stand_lon": namelist["geogrid"]["stand_lon"],
        "map_proj": namelist["geogrid"]["map_proj"]
    }

    return domain_setting


__all__ = ["DomainSetting", "create_projection", "parse_domain_setting"]
