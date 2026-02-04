"""
wrfrun.model.plot
#################

This module is used to plot domain area so users can check their domain settings before running simulation.

.. autosummary::
    :toctree: generated/

    _calculate_x_y_offset
    create_projection
    parse_domain_setting
    plot_domain_area
    generate_domain_area
"""

from os.path import abspath, exists
from typing import Union

import cartopy.feature as cfeature
import f90nml
import matplotlib.pyplot as plt
from cartopy import crs
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from haversine.haversine import Direction, Unit, inverse_haversine
from matplotlib.figure import Figure

from ..core import WRFRUN
from ..log import logger
from ..utils import check_path
from .type import DomainSetting


def _calculate_x_y_offset(domain_settings: DomainSetting) -> tuple[float, float]:
    """
    Calculate X and Y offset from planar origin in metres.

    :param domain_settings: Dictionary contains domain settings.
    :type domain_settings: DomainSetting | None
    :return: (X offset, Y offset)
    :rtype: tuple
    """
    false_easting = (domain_settings["points_x"][0] - 1) / 2 * domain_settings["resolution_x"]
    false_northing = (domain_settings["points_y"][0] - 1) / 2 * domain_settings["resolution_y"]
    return false_easting, false_northing


def create_projection(
    domain_settings: DomainSetting,
) -> Union[crs.LambertConformal, crs.NorthPolarStereo, crs.SouthPolarStereo, crs.Mercator, crs.PlateCarree]:
    """
    Create a projection from domain settings which can be used to draw images.

    You can give your custom domain settings to create the projection.
    Please see ``wrfrun.mode.plot.DomainSetting`` for more information about ``domain_settings``.

    :param domain_settings: Dictionary contains domain settings.
    :type domain_settings: DomainSetting
    :return: Projection object and the used domain settings.
    :rtype: (Projection, domain settings)
    """
    # declare the proj to pass static type check
    proj = None

    match domain_settings["projection_type"]:
        case "lat-lon":
            proj = crs.PlateCarree(central_longitude=domain_settings["reference_lon"])

        case "lambert":
            false_easting, false_northing = _calculate_x_y_offset(domain_settings)
            proj = crs.LambertConformal(
                central_longitude=domain_settings["reference_lon"],
                central_latitude=domain_settings["reference_lat"],
                standard_parallels=(domain_settings["true_lat1"], domain_settings["true_lat2"]),
                false_easting=false_easting,
                false_northing=false_northing,
            )

        case "polar":
            ref_lat = domain_settings["reference_lat"]
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
                central_longitude=domain_settings["reference_lon"],
                latitude_true_scale=domain_settings["true_lat1"],
                # false_northing=false_northing,
                # false_easting=false_easting
            )

    if proj is not None:
        return proj

    else:
        logger.error(f"Unknown projection name: {domain_settings['projection_type']}")
        raise KeyError(f"Unknown projection name: {domain_settings['projection_type']}")


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


def plot_domain_area(fig: Figure, domain_settings: DomainSetting):
    """
    Plot domain area based on domain settings.

    **WARNING**

    This function is still unstable, result may be different from the ncl.

    :param fig: Figure to plot domain.
    :type fig: Figure
    :param domain_settings: Dictionary contains domain settings. If None, read domain settings from ``WRFRUNConfig``.
    :type domain_settings: DomainSetting | None
    """
    proj = create_projection(domain_settings)

    fig.clear()
    ax: GeoAxes = fig.add_subplot(1, 1, 1, projection=proj)  # type: ignore
    ax.coastlines(resolution="50m")
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)

    # set gridline attributes, close the default labels
    grid_line = ax.gridlines(
        draw_labels=True,
        dms=True,
        linestyle=":",
        linewidth=0.3,
        x_inline=False,
        y_inline=False,
        color="k",
        rotate_labels=None,
        xformatter=LONGITUDE_FORMATTER,
        yformatter=LATITUDE_FORMATTER,
    )

    # close coordinates labels on the top and right
    grid_line.top_labels = False
    grid_line.right_labels = False

    ax.set_title("Domain Configuration")

    # set area range
    if isinstance(proj, crs.Mercator):
        # we may need to calculate the range of longitude and latitude
        ref_lon = domain_settings["reference_lon"]
        ref_lat = domain_settings["reference_lat"]
        false_easting, false_northing = _calculate_x_y_offset(domain_settings)
        _, start_lon = inverse_haversine((ref_lat, ref_lon), false_easting, direction=Direction.WEST, unit=Unit.METERS)
        _, end_lon = inverse_haversine((ref_lat, ref_lon), false_easting, direction=Direction.EAST, unit=Unit.METERS)
        start_lat, _ = inverse_haversine((ref_lat, ref_lon), false_northing, direction=Direction.SOUTH, unit=Unit.METERS)
        end_lat, _ = inverse_haversine((ref_lat, ref_lon), false_northing, direction=Direction.NORTH, unit=Unit.METERS)
        ax.set_extent([start_lon, end_lon, start_lat, end_lat])

    elif isinstance(proj, crs.LambertConformal):
        false_easting, false_northing = _calculate_x_y_offset(domain_settings)
        ax.set_extent([0, false_easting * 2, 0, false_northing * 2], crs=proj)

    else:
        logger.error(f"Unsupported project type: {type(proj)}")


def generate_domain_area():
    """
    Generate domain area for each model based on user's config.
    Images are saved to the output directory with name: "${model_name}_domain.png".

    :return: True if domain area is ploted, else False.
    :rtype: bool
    """
    WRFRUNConfig = WRFRUN.config
    save_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)
    check_path(save_path)
    save_path = abspath(save_path)

    fig = plt.figure(figsize=(10.24, 10.24))

    flag = False

    model_configs = WRFRUNConfig["model"]
    for model_name in model_configs:
        if model_name in ["wrf"] and model_configs[model_name]["use"]:
            namelist = model_configs[model_name]
            plot_domain_area(fig, parse_domain_setting(namelist))

            _save_path = f"{save_path}/{model_name}_domain.png"
            fig.savefig(_save_path)

            logger.info(f"Save domain image for '{model_name}' to '{_save_path}'")

            flag = True

    return flag


__all__ = ["plot_domain_area", "create_projection", "generate_domain_area"]
