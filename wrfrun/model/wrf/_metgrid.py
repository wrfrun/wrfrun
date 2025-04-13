from os import listdir
from os.path import exists
from typing import Dict

from xarray import open_dataset

from wrfrun.core import WRFRUNConfig
from wrfrun.utils import logger


def get_metgrid_levels(nc_file: str) -> Dict[str, int]:
    """Read metgrid output file and get metgrid levels, land cat and metgrid soil levels

    Args:
        nc_file (str): Output nc file path

    Returns:
        Dict[str, int]: {num_metgrid_levels: number, num_land_cat: number, num_metgrid_soil_level: number}
    """
    # check file
    if not exists(nc_file):
        logger.error(f"File {nc_file} not exists")
        raise FileNotFoundError

    # read data
    dataset = open_dataset(nc_file)

    # read variables
    num_metgrid_levels = dataset["num_metgrid_levels"].size
    num_land_cat = dataset.attrs["NUM_LAND_CAT"]
    num_metgrid_soil_levels = dataset.attrs["NUM_METGRID_SOIL_LEVELS"]

    return dict(
        num_metgrid_levels=num_metgrid_levels,
        num_land_cat=num_land_cat,
        num_metgrid_soil_levels=num_metgrid_soil_levels
    )


def reconcile_namelist_metgrid(metgrid_path: str):
    """
    There are some settings in WRF namelist that are affected by metgrid output, for example, ``num_metgrid_levels``.
    Namelist should be checked and modified before be used by WRF.

    :param metgrid_path: The path store output from metgrid.exe.
                         If it is None, the default output path will be used.
    :type metgrid_path: str
    :return:
    :rtype:
    """
    logger.info(f"Checking values in WRF namelist and metgrid output ...")
    metgrid_output_name = [x for x in listdir(metgrid_path) if x.endswith(".nc")]
    metgrid_output_name.sort()
    metgrid_output_name = metgrid_output_name[0]

    metgrid_levels = get_metgrid_levels(f"{metgrid_path}/{metgrid_output_name}")

    update_values = {
        "domains": {
            "num_metgrid_levels": metgrid_levels["num_metgrid_levels"],
            "num_metgrid_soil_levels": metgrid_levels["num_metgrid_soil_levels"],
        },
        "physics": {
            "num_land_cat": metgrid_levels["num_land_cat"]
        }
    }

    WRFRUNConfig.update_namelist(update_values, "wrf")


__all__ = ["get_metgrid_levels", "reconcile_namelist_metgrid"]
