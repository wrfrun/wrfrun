import logging
from typing import Literal, Optional, TypedDict, Union

from cartopy import crs

from wrfrun import WRFRUNConfig


logger = logging.getLogger("wrfrun")


class ProjectionSetting(TypedDict):
    """
    Projection settings.
    """
    name: Literal["lambert", "polar", "mercator", "lat-lon"]
    settings: dict


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
    map_proj: ProjectionSetting
    ref_lat: Union[int, float]
    ref_lon: Union[int, float]


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
            "map_proj": {
                "name": user_settings["map_proj"]["name"],
                "settings": user_settings["map_proj"],
            }
        }

    match domain_settings["map_proj"]["name"]:
        case "lat-lon":
            proj = crs.PlateCarree(central_longitude=domain_settings["ref_lon"])
        case "lambert":
            false_easting = (domain_settings["e_we"][0] - 1) / 2 * domain_settings["dx"]
            false_northing = (domain_settings["e_sn"][0] - 1) / 2 * domain_settings["dy"]
            proj = crs.LambertConformal(
                central_longitude=domain_settings["ref_lon"],
                central_latitude=domain_settings["ref_lat"],
                standard_parallels=(
                    domain_settings["map_proj"]["settings"]["true_lat1"],
                    domain_settings["map_proj"]["settings"]["true_lat2"]
                ),
                false_easting=false_easting,
                false_northing=false_northing
            )
        case _:
            logger.error(f"Unknown projection name: {domain_settings['map_proj']['name']}")
            raise KeyError(f"Unknown projection name: {domain_settings['map_proj']['name']}")

    return proj


__all__ = ["ProjectionSetting", "DomainSetting", "create_projection"]
