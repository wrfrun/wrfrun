from os import listdir
from os.path import exists
from typing import Dict

from xarray import open_dataset

from wrfrun import WRFRUNConfig
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


def process_after_ndown():
    """
    After running ndown.exe, namelist settings are supposed to be changed,
    so WRF can simulate a higher resolution domain according to `WRF User's Guide <https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/running_wrf.html#wrf-nesting>`_.
    `wrfrun` provide this function to help you change these settings which have multiple values for each domain.
    The first value will be removed to ensure the value of higher resolution domain is the first value.

    :return:
    """
    namelist_data = WRFRUNConfig.get_namelist("wrf")

    for section in namelist_data:
        if section in ["bdy_control", "namelist_quilt"]:
            continue

        for key in namelist_data[section]:
            if key in ["grid_id", "parent_id", "i_parent_start", "j_parent_start", "parent_grid_ratio", "parent_time_step_ratio", "eta_levels"]:
                continue

            if isinstance(namelist_data[section][key], list):

                if len(namelist_data[section][key]) > 1:
                    namelist_data[section][key] = namelist_data[section][key][1:]

    namelist_data["domains"]["max_dom"] = 1

    time_ratio = namelist_data["domains"]["parent_time_step_ratio"][1]
    namelist_data["domains"]["time_step"] = namelist_data["domains"]["time_step"] // time_ratio

    WRFRUNConfig.update_namelist(namelist_data, "wrf")

    logger.info(f"Update namelist after running ndown.exe")


__all__ = ["reconcile_namelist_metgrid", "get_metgrid_levels", "process_after_ndown"]
