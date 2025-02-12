from typing import Tuple

from cartopy import crs
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.collections import QuadMesh
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from netCDF4 import Dataset  # type: ignore
from wrf import getvar, latlon_coords, get_cartopy, to_np
from xarray import DataArray

from wrfrun.utils import logger

# Here defines the colormap for landuse and soiltype
LANDUSE_CMAP = ListedColormap([
    [0, .4, 0],         # 1 Evergreen Needleleaf Forest
    [0, .4, .2],        # 2 Evergreen Broadleaf Forest
    [.2, .8, .2],       # 3 Deciduous Needleleaf Forest
    [.2, .8, .4],       # 4 Deciduous Broadleaf Forest
    [.2, .6, .2],       # 5 Mixed Forests
    [.3, .7, 0],        # 6 Closed Shrublands
    [.82, .41, .12],    # 7 Open Shurblands
    [.74, .71, .41],    # 8 Woody Savannas
    [1, .84, .0],       # 9 Savannas
    [0, 1, 0],          # 10 Grasslands
    [0, 1, 1],          # 11 Permanant Wetlands
    [1, 1, 0],          # 12 Croplands
    [1, 0, 0],          # 13 Urban and Built-up
    [.7, .9, .3],       # 14 Cropland/Natual Vegation Mosaic
    [1, 1, 1],          # 15 Snow and Ice
    [.914, .914, .7],   # 16 Barren or Sparsely Vegetated
    [.5, .7, 1],        # 17 Water (like oceans)
    [.86, .08, .23],    # 18 Wooded Tundra
    [.97, .5, .31],     # 19 Mixed Tundra
    [.91, .59, .48],    # 20 Barren Tundra
    [0, 0, .88],        # 21 Lake
])

LANDUSE_LABELS = [
    'Evergreen Needleleaf Forest',
    'Evergreen Broadleaf Forest',
    'Deciduous Needleleaf Forest',
    'Deciduous Broadleaf Forest',
    'Mixed Forests',
    'Closed Shrublands',
    'Open Shrublands',
    'Woody Savannas',
    'Savannas',
    'Grasslands',
    'Permanent Wetlands',
    'Croplands',
    'Urban and Built-Up',
    'Cropland/Natural Vegetation Mosaic',
    'Snow and Ice',
    'Barren or Sparsely Vegetated',
    'Water',
    'Wooded Tundra',
    'Mixed Tundra',
    'Barren Tundra',
    'Lake',
]


# Here defines the colormap and labels for soil type
SOILTYPE_CMAP = ListedColormap([
    [0, .4, 0],         # 1 Sand
    [0, .4, .2],        # 2 Loamy Sand
    [.2, .8, .2],       # 3 Sandy Loam
    [.2, .8, .4],       # 4 Silt Loam
    [.2, .6, .2],       # 5 Silt
    [.3, .7, 0],        # 6 Loam
    [.82, .41, .12],    # 7 Sandy Clay Loam
    [.74, .71, .41],    # 8 Silty Clay Loam
    [1, .84, .0],       # 9 Clay Loam
    [0, 1, 0],          # 10 Sandy Clay
    [0, 1, 1],          # 11 Silty Clay
    [1, 1, 0],          # 12 Clay
    [1, 0, 0],          # 13 Organic Material
    [.7, .9, .3],       # 14 Water
    [1, 1, 1],          # 15 Bedrock
    [.914, .914, .7]    # 16 Other
])

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
    "Other"
]


def get_cmap_ticks(name: str) -> tuple:
    """Get corresponding colormap, labels and ticks.

    Args:
        name (str): Field name.

    Returns:
        tuple: (colormap, labels, ticks)
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
    """Draw specific data in geo_em*

    Args:
        data_path (str): data path.
        field (str): Which field you want to draw.
        fig (Figure): Matplotlib figure object.
        nrow (int): Row number of axes.
        ncol (int): Column number of axes.
        index (int): Index of axes.
    """
    # take out data
    data: DataArray = getvar(Dataset(data_path), field)     # type: ignore

    # soiltype data is different from landuse data
    if field in ["SOILCTOP", "SOILCBOT"]:
        data = data.argmax(dim="soil_cat", keep_attrs=True)     # type: ignore
        # get data attrs
        data_attrs = data.attrs
        data = data + 1
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
    data, lats, lons = to_np(data), to_np(lats), to_np(lons)    # type: ignore

    # plot
    im = ax.pcolormesh(
        lons, lats, data, vmin=1, vmax=len(labels) + 1, cmap=cmap, transform=crs.PlateCarree()
    )

    return ax, im   # type: ignore


__all__ = ["draw_geogrid", "get_cmap_ticks"]
