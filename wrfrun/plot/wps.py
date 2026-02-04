"""
wrfrun.plot.wps
###############

Functions to plot outputs of ``geogrid.exe``.

.. autosummary::
    :toctree: generated/

    get_cmap_ticks
    draw_geogrid
"""

from typing import Tuple

from cartopy import crs
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.collections import QuadMesh
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from netCDF4 import Dataset  # type: ignore
from xarray import DataArray

from wrfrun.log import logger

# Here defines the colormap for landuse and soiltype
LANDUSE_CMAP = ListedColormap(
    (
        [0, 0.4, 0],  # 1: Evergreen Needleleaf Forest
        [0, 0.4, 0.2],  # 2: Evergreen Broadleaf Forest
        [0.2, 0.8, 0.2],  # 3: Deciduous Needleleaf Forest
        [0.2, 0.8, 0.4],  # 4: Deciduous Broadleaf Forest
        [0.2, 0.6, 0.2],  # 5: Mixed Forests
        [0.3, 0.7, 0],  # 6: Closed Shrublands
        [0.82, 0.41, 0.12],  # 7: Open Shurblands
        [0.74, 0.71, 0.41],  # 8: Woody Savannas
        [1, 0.84, 0.0],  # 9: Savannas
        [0, 1, 0],  # 10: Grasslands
        [0, 1, 1],  # 11: Permanent Wetlands
        [1, 1, 0],  # 12: Croplands
        [1, 0, 0],  # 13: Urban and Built-up
        [0.7, 0.9, 0.3],  # 14: Cropland/Natual Vegation Mosaic
        [1, 1, 1],  # 15: Snow and Ice
        [0.914, 0.914, 0.7],  # 16: Barren or Sparsely Vegetated
        [0.5, 0.7, 1],  # 17: Water (like oceans)
        [0.86, 0.08, 0.23],  # 18: Wooded Tundra
        [0.97, 0.5, 0.31],  # 19: Mixed Tundra
        [0.91, 0.59, 0.48],  # 20: Barren Tundra
        [0, 0, 0.88],  # 21: Lake
    )
)

LANDUSE_LABELS = [
    "Evergreen Needleleaf Forest",
    "Evergreen Broadleaf Forest",
    "Deciduous Needleleaf Forest",
    "Deciduous Broadleaf Forest",
    "Mixed Forests",
    "Closed Shrublands",
    "Open Shrublands",
    "Woody Savannas",
    "Savannas",
    "Grasslands",
    "Permanent Wetlands",
    "Croplands",
    "Urban and Built-Up",
    "Cropland/Natural Vegetation Mosaic",
    "Snow and Ice",
    "Barren or Sparsely Vegetated",
    "Water",
    "Wooded Tundra",
    "Mixed Tundra",
    "Barren Tundra",
    "Lake",
]


# Here defines the colormap and labels for soil types
SOILTYPE_CMAP = ListedColormap(
    (
        [0, 0.4, 0],  # 1: Sand
        [0, 0.4, 0.2],  # 2: Loamy Sand
        [0.2, 0.8, 0.2],  # 3: Sandy Loam
        [0.2, 0.8, 0.4],  # 4: Silt Loam
        [0.2, 0.6, 0.2],  # 5: Silt
        [0.3, 0.7, 0],  # 6: Loam
        [0.82, 0.41, 0.12],  # 7: Sandy Clay Loam
        [0.74, 0.71, 0.41],  # 8: Silty Clay Loam
        [1, 0.84, 0.0],  # 9: Clay Loam
        [0, 1, 0],  # 10: Sandy Clay
        [0, 1, 1],  # 11: Silty Clay
        [1, 1, 0],  # 12: Clay
        [1, 0, 0],  # 13: Organic Material
        [0.7, 0.9, 0.3],  # 14: Water
        [1, 1, 1],  # 15: Bedrock
        [0.914, 0.914, 0.7],  # 16: Other
    )
)

SOILTYPE_LABELS = [
    "Sand",
    "Loamy Sand",
    "Sandy Loam",
    "Silt Loam",
    "Silt",
    "Loam",
    "Sandy Clay Loam",
    "Silty Clay Loam",
    "Clay Loam",
    "Sandy Clay",
    "Silty Clay",
    "Clay",
    "Organic Material",
    "Water",
    "Bedrock",
    "Other",
]


def get_cmap_ticks(name: str) -> tuple:
    """
    Get corresponding colormap, labels and ticks.

    :param name: File name.
    :type name: str
    :return: (colormap, labels, ticks)
    :rtype: tuple
    """
    # name map
    cmap_ticks_map = {
        "LU_INDEX": {
            "cmap": LANDUSE_CMAP,
            "labels": LANDUSE_LABELS,
        },
        "SOILCTOP": {
            "cmap": SOILTYPE_CMAP,
            "labels": SOILTYPE_LABELS,
        },
        "SOILCBOT": {
            "cmap": SOILTYPE_CMAP,
            "labels": SOILTYPE_LABELS,
        },
    }

    # take out colormap and labels
    if name not in cmap_ticks_map:
        logger.error(f"Can't found colormap and labels for {name}")
        raise ValueError

    cmap = cmap_ticks_map[name]["cmap"]
    labels = cmap_ticks_map[name]["labels"]

    # generate ticks
    ticks = [x + 1.5 for x in range(len(labels))]

    return cmap, labels, ticks


def draw_geogrid(data_path: str, field: str, fig: Figure, nrow: int, ncol: int, index: int) -> Tuple[GeoAxes, QuadMesh]:
    """
    Draw specific data in geogrid outputs.

    :param data_path: Data path.
    :type data_path: str
    :param field: Which field you want to draw.
    :type field: str
    :param fig: Matplotlib figure object.
    :type fig: Figure
    :param nrow: Row number of axes.
    :type nrow: int
    :param ncol: Column number of axes.
    :type ncol: int
    :param index: Index of axes.
    :type index: int
    :return: (GeoAxes, QuadMesh)
    :rtype: tuple
    """
    # lazy import
    try:
        from wrf import get_cartopy, getvar, latlon_coords, to_np

    except ImportError:
        logger.error("Currently `wrf-python` isn't list as `wrfrun` dependency.")
        logger.error("You need to install `wrf-python` package to use this feature.")
        exit(1)

    # take out data
    data: DataArray = getvar(Dataset(data_path), field)  # type: ignore

    # soiltype data is different from landuse data
    if field in ["SOILCTOP", "SOILCBOT"]:
        data = data.argmax(dim="soil_cat", keep_attrs=True)  # type: ignore
        # get data attrs
        data_attrs = data.attrs
        data = data + 1  # type: ignore
        data.attrs = data_attrs

    # get latitude and longitude
    lats, lons = latlon_coords(data)

    # get projection
    proj = get_cartopy(data)

    # add axes
    ax = fig.add_subplot(nrow, ncol, index, projection=proj)

    # get colormap, labels and ticks
    cmap, labels, ticks = get_cmap_ticks(field)

    # convert data to numpy
    data, lats, lons = to_np(data), to_np(lats), to_np(lons)  # type: ignore

    # plot
    im = ax.pcolormesh(lons, lats, data, vmin=1, vmax=len(labels) + 1, cmap=cmap, transform=crs.PlateCarree())

    return ax, im  # type: ignore


__all__ = ["draw_geogrid", "get_cmap_ticks"]
