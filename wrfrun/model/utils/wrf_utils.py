from os import listdir
from shutil import move

from wrfrun.core import WRFRUNConfig, WRFRUNConstants, WRFRUNNamelist
from wrfrun.utils import check_path, logger
from .wps_utils import get_metgrid_levels


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

    WRFRUNNamelist.update_namelist(update_values, "wrf")


def clear_wrf_logs():
    """
    This function can automatically collect WRF log files and save them to ``output_path``.
    This function is used inside the wrfrun package.
    If you want to do something about the log files, check the corresponding code of interface functions in ``wrfrun.model.run``.

    :return:
    :rtype:
    """
    wrf_status = WRFRUNConstants.get_wrf_status()
    wrf_work_path = WRFRUNConstants.get_work_path("wrf")

    log_files = [x for x in listdir(wrf_work_path) if x.startswith("rsl.")]

    if len(log_files) > 0:
        logger.warning(f"Found unprocessed log files of {wrf_status}")

        log_save_path = f"{WRFRUNConfig.get_output_path()}/{wrf_status}/logs"
        check_path(log_save_path)

        for _file in log_files:
            move(f"{wrf_work_path}/{_file}", f"{log_save_path}/{_file}")

        logger.warning(f"Unprocessed log files of {wrf_status} has been saved to {log_save_path}, check it")


__all__ = ["reconcile_namelist_metgrid", "clear_wrf_logs"]
