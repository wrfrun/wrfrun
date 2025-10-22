from os.path import abspath, exists
from typing import Literal, Optional, TypedDict, Union

import cartopy.feature as cfeature
import f90nml
import matplotlib.pyplot as plt
from cartopy import crs
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from haversine.haversine import Direction, Unit, inverse_haversine

from wrfrun.core import WRFRUNConfig
from wrfrun.utils import check_path, logger


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
    
    
def _calculate_x_y_offset(domain_settings: DomainSetting) -> tuple[float, float]:
    """
    Calculate X and Y offset from planar origin in metres.

    :param domain_settings: Dictionary contains domain settings.
    :type domain_settings: DomainSetting | None
    :return: (X offset, Y offset)
    :rtype: tuple
    """
    false_easting = (domain_settings["e_we"][0] - 1) / 2 * domain_settings["dx"]
    false_northing = (domain_settings["e_sn"][0] - 1) / 2 * domain_settings["dy"]
    return false_easting, false_northing


def create_projection(domain_settings: DomainSetting) -> crs.Projection:
    """
    Create a projection from domain settings which can be used to draw images.

    You can give your custom domain settings to create the projection.
    Please see ``wrfrun.mode.plot.DomainSetting`` for more information about ``domain_settings``.

    :param domain_settings: Dictionary contains domain settings.
    :type domain_settings: DomainSetting
    :return: Projection object and the used domain settings.
    :rtype: (Projection, domain settings)
    """
    match domain_settings["map_proj"]:

        case "lat-lon":
            proj = crs.PlateCarree(central_longitude=domain_settings["ref_lon"])

        case "lambert":
            false_easting, false_northing = _calculate_x_y_offset(domain_settings)
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
            # false_easting, false_northing = _calculate_x_y_offset(domain_settings)
            # central_longitude = domain_settings["ref_lon"]
            # central_latitude = domain_settings["ref_lat"]
            # ref_lat_distance = haversine(
            #     (0, central_longitude),
            #     (central_latitude, central_longitude),
            #     unit=Unit.METERS
            # )
            # ref_lat_distance = ref_lat_distance if central_latitude < 0 else -ref_lat_distance
            # false_northing = ref_lat_distance + false_northing
            proj = crs.Mercator(
                central_longitude=domain_settings["ref_lon"],
                latitude_true_scale=domain_settings["truelat1"],
                # false_northing=false_northing,
                # false_easting=false_easting
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


def plot_domain_area(
    fig: plt.Figure,
    domain_settings: Optional[DomainSetting] = None,
    model_name: Optional[str] = None
):
    """
    Plot domain area based on domain settings.

    **WARNING**

    This function is still unstable, result may be different from the ncl.

    :param fig: Figure to plot domain.
    :type fig: Figure
    :param domain_settings: Dictionary contains domain settings. If None, read domain settings from ``WRFRUNConfig``.
    :type domain_settings: DomainSetting | None
    :param model_name: Model's name for reading domain settings.
    :type model_name: str | None
    """
    if domain_settings is None:
        if model_name is None:
            logger.error("You need to give 'model_name' if `domain_settings == None`")
            raise ValueError("You need to give 'model_name' if `domain_settings == None`")

        user_settings = WRFRUNConfig.get_model_config(model_name)["domain"]
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
            "map_proj": user_settings["map_proj"]
        }

    proj = create_projection(domain_settings)

    fig.clear()
    ax: GeoAxes = fig.add_subplot(1, 1, 1, projection=proj)     # type: ignore
    ax.coastlines(resolution="50m")
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)

    # set gridline attributes, close the default labels
    grid_line = ax.gridlines(
        draw_labels=True, dms=True, linestyle=":", linewidth=0.3,
        x_inline=False, y_inline=False, color='k'
    )

    # close coordinates labels on the top and right
    grid_line.top_labels = False
    grid_line.right_labels = False

    # align coordinates labels
    grid_line.rotate_labels = None

    # set label formatter
    grid_line.xformattter = LONGITUDE_FORMATTER
    grid_line.yformatter = LATITUDE_FORMATTER
    ax.set_title("Domain Configuration")

    # set area range
    match type(proj):

        case crs.Mercator:
            # we may need to calculate the range of longitude and latitude
            ref_lon = domain_settings["ref_lon"]
            ref_lat = domain_settings["ref_lat"]
            false_easting, false_northing = _calculate_x_y_offset(domain_settings)
            _, start_lon = inverse_haversine((ref_lat, ref_lon), false_easting, direction=Direction.WEST, unit=Unit.METERS)
            _, end_lon = inverse_haversine((ref_lat, ref_lon), false_easting, direction=Direction.EAST, unit=Unit.METERS)
            start_lat, _ = inverse_haversine((ref_lat, ref_lon), false_northing, direction=Direction.SOUTH, unit=Unit.METERS)
            end_lat, _ = inverse_haversine((ref_lat, ref_lon), false_northing, direction=Direction.NORTH, unit=Unit.METERS)
            ax.set_extent([start_lon, end_lon, start_lat, end_lat])

        case _:
            logger.error(f"Unsupported project type: {type(proj)}")


def generate_domain_area():
    """
    Generate domain area for each model based on user's config.
    Images are saved to the output directory with name: "${model_name}_domain.png".

    :return:
    :rtype:
    """
    save_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)
    check_path(save_path)
    save_path = abspath(save_path)

    fig = plt.figure(figsize=(10.24, 10.24))

    model_configs = WRFRUNConfig["model"]
    for model_name in model_configs:
        plot_domain_area(fig, model_name=model_name)

        _save_path = f"{save_path}/{model_name}_domain.png"
        fig.savefig(_save_path)

        logger.info(f"Save domain image for '{model_name}' to '{_save_path}'")


__all__ = ["plot_domain_area", "DomainSetting", "create_projection", "parse_domain_setting", "generate_domain_area"]
