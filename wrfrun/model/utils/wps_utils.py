from os import listdir
from os.path import abspath, basename, dirname, exists
from shutil import move
from typing import Dict, List, OrderedDict, Union

from xarray import open_dataset

from wrfrun.core import WRFRUNConfig, WRFRUNConstants, WRFRUNNamelist
from wrfrun.utils import check_domain_shape, check_path, logger, rectify_domain_size


def _update_namelist_hook(namelist_data: Union[OrderedDict, dict]) -> Union[OrderedDict, dict]:
    """Hook function to check namelist after update namelist based on user namelist.

    Args:
        namelist_data (Union[OrderedDict, dict]): Namelist data.

    Returns:
        Union[OrderedDict, dict]: Namelist data.
    """
    # check domain size hook
    # get parent grid ratio
    parent_grid_ratio = namelist_data["geogrid"]["parent_grid_ratio"]
    # get e_we and e_sn
    e_we = namelist_data["geogrid"]["e_we"]
    e_sn = namelist_data["geogrid"]["e_sn"]
    # new e_we and e_sn
    new_e_we = []
    new_e_sn = []
    # check e_we
    for ratio, x_size, y_size in zip(parent_grid_ratio, e_we, e_sn):
        if check_domain_shape(x_size, y_size, ratio) != (True, True):
            logger.warn(
                f"Your domain shape need to be rectified because: (({x_size}, {y_size}) - 1) % {ratio} != 0")
            new_e_we.append(rectify_domain_size(x_size, ratio))
            new_e_sn.append(rectify_domain_size(y_size, ratio))
            logger.warn(
                f"Rectified shape is: ({new_e_we[-1]}, {new_e_sn[-1]})")
        else:
            new_e_we.append(x_size)
            new_e_sn.append(y_size)
    # update
    namelist_data["geogrid"]["e_we"] = new_e_we
    namelist_data["geogrid"]["e_sn"] = new_e_sn

    return namelist_data


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


def get_wif_dir() -> str:
    """
    Get the output directory of WRF intermediate file (wif).

    :return: Absolute path.
    """
    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")
    wif_path = WRFRUNNamelist.get_namelist("wps")["ungrib"]["prefix"]
    wif_path = abspath(f"{WPS_WORK_PATH}/{dirname(wif_path)}")
    return wif_path


def get_wif_prefix() -> str:
    """
    Get the prefix string of WRF intermediate file (wif).

    :return: Prefix string of WRF intermediate file (wif).
    """
    wif_prefix = WRFRUNNamelist.get_namelist("wps")["ungrib"]["prefix"]
    wif_prefix = basename(wif_prefix)
    return wif_prefix


def set_wif_prefix(prefix: str):
    """
    Update the prefix string of WRF intermediate file (wif).
    This function changes the prefix value of section ungrib in the file namelist.wps.

    :param prefix: Prefix string of WIF.
                   For example, "SST_FILE".
    :return:
    """
    WRFRUNNamelist.update_namelist({
        "ungrib": {"prefix": f"./outputs/{prefix}"}
    }, "wps")


def get_fg_names() -> List[str]:
    """
    Extract prefix strings from "fg_name" in namelist "metgrid" section.

    :return: Prefix strings list.
    :rtype: list
    """
    fg_names = WRFRUNNamelist.get_namelist("wps")["metgrid"]["fg_name"]
    fg_names = [basename(x) for x in fg_names]
    return fg_names


def set_fg_names(fg_names: List[str]):
    """
    Set prefix strings of "fg_name" in namelist "metgrid" section.

    :param fg_names: Prefix strings list.
    :type fg_names: list
    :return:
    :rtype:
    """
    fg_names = [f"./outputs/{x}" for x in fg_names]
    WRFRUNNamelist.update_namelist({
        "metgrid": {"fg_name": fg_names}
    }, "wps")


def clear_wps_logs():
    """
    This function can automatically collect WRF log files and save them to ``output_path``.
    This function is used inside the wrfrun package.
    If you want to do something about the log files, check the corresponding code of interface functions in ``wrfrun.model.run``.

    :return:
    :rtype:
    """
    wrf_status = WRFRUNConstants.get_wrf_status()
    wps_work_path = WRFRUNConstants.get_work_path("wps")

    log_files = [x for x in listdir(wps_work_path) if ".log" in x]

    if len(log_files) > 0:
        logger.warning(f"Found unprocessed log files of {wrf_status}")

        log_save_path = f"{WRFRUNConfig.get_output_path()}/{wrf_status}/logs"
        check_path(log_save_path)

        for _file in log_files:
            move(f"{wps_work_path}/{_file}", f"{log_save_path}/{_file}")

        logger.warning(f"Unprocessed log files of {wrf_status} has been saved to {log_save_path}, check it")


__all__ = ["get_metgrid_levels", "set_wif_prefix", "get_wif_dir", "get_wif_prefix", "get_fg_names", "set_fg_names", "clear_wps_logs"]
