from datetime import datetime, timedelta
from os.path import exists, dirname, basename
from typing import Union

from wrfrun.core import WRFRUNConfig
from wrfrun.res import NAMELIST_DFI, NAMELIST_WPS, NAMELIST_WRF, NAMELIST_WRFDA
from wrfrun.utils import logger
from wrfrun.workspace.wrf import WORKSPACE_MODEL_WPS
from .scheme import *


UNGRIB_OUTPUT_DIR = "./outputs"


def get_ungrib_out_dir_path() -> str:
    """
    Get the output directory of ungrib output (WRF intermediate file).

    :return: URI path.
    :rtype: str
    """
    wif_prefix = WRFRUNConfig.get_namelist("wps")["ungrib"]["prefix"]
    wif_path = f"{WORKSPACE_MODEL_WPS}/{dirname(wif_prefix)}"

    return wif_path


def get_ungrib_out_prefix() -> str:
    """
    Get the prefix string of ungrib output (WRF intermediate file).

    :return: Prefix string of ungrib output (WRF intermediate file).
    :rtype: str
    """
    wif_prefix = WRFRUNConfig.get_namelist("wps")["ungrib"]["prefix"]
    wif_prefix = basename(wif_prefix)
    return wif_prefix


def set_ungrib_out_prefix(prefix: str):
    """
    Set the prefix string of ungrib output (WRF intermediate file).

    :param prefix: Prefix string of ungrib output (WRF intermediate file).
    :type prefix: str
    """
    WRFRUNConfig.update_namelist(
        {
            "ungrib": {"prefix": f"{UNGRIB_OUTPUT_DIR}/{prefix}"}
        }, "wps"
    )


def get_metgrid_fg_names() -> list[str]:
    """
    Get prefix strings from "fg_name" in namelist "metgrid" section.

    :return: Prefix strings list.
    :rtype: list
    """
    fg_names = WRFRUNConfig.get_namelist("wps")["metgrid"]["fg_name"]
    fg_names = [basename(x) for x in fg_names]
    return fg_names


def set_metgrid_fg_names(prefix: Union[str, list[str]]):
    """
    Set prefix strings of "fg_name" in namelist "metgrid" section.

    :param prefix: Prefix strings list.
    :type prefix: str | list
    """
    if isinstance(prefix, str):
        prefix = [prefix, ]
    fg_names = [f"{UNGRIB_OUTPUT_DIR}/{x}" for x in prefix]
    WRFRUNConfig.update_namelist(
        {
            "metgrid": {"fg_name": fg_names}
        }, "wps"
    )


def _check_start_end_date(max_dom: int, start_date: Union[datetime, list[datetime]], end_date: Union[datetime, list[datetime]]) -> tuple[list[datetime], list[datetime]]:
    """
    Format start date and end date.

    :param max_dom: Domain number.
    :type max_dom: int
    :param start_date: Date list parsed from the config file.
    :type start_date: datetime | list
    :param end_date: Date list parsed from the config file.
    :type end_date: datetime | list
    :return: Formated date list.
    :rtype: list
    """
    if isinstance(start_date, datetime):
        start_date = [start_date for _ in range(max_dom)]
    elif isinstance(start_date, list):
        if len(start_date) != max_dom:
            logger.error(f"You have {max_dom} domains, but you only give {len(start_date)} dates for `start_date`.")
            raise ValueError(f"You have {max_dom} domains, but you only give {len(start_date)} dates for `start_date`.")

    if isinstance(end_date, datetime):
        end_date = [end_date for _ in range(max_dom)]
    elif isinstance(end_date, list):
        if len(end_date) != max_dom:
            logger.error(f"You have {max_dom} domains, but you only give {len(end_date)} dates for `start_date`.")
            raise ValueError(f"You have {max_dom} domains, but you only give {len(end_date)} dates for `start_date`.")

    return start_date, end_date


def prepare_wps_namelist():
    """
    This function read WPS template namelist and update its value based on the config file and user custom namelist.

    """
    # prepare namelist
    WRFRUNConfig.read_namelist(WRFRUNConfig.parse_resource_uri(NAMELIST_WPS), "wps")
    wrf_config = WRFRUNConfig.get_model_config("wrf")

    # get domain number
    max_dom = wrf_config["domain"]["domain_num"]

    # get start_date and end_date
    start_date = wrf_config["time"]["start_date"]
    end_date = wrf_config["time"]["end_date"]

    start_date, end_date = _check_start_end_date(max_dom, start_date, end_date)
    start_date = [x.strftime("%Y-%m-%d_%H:%M:%S") for x in start_date]
    end_date = [x.strftime("%Y-%m-%d_%H:%M:%S") for x in end_date]

    # get input data time interval
    interval_seconds = wrf_config["time"]["input_data_interval"]

    # generate update settings based on the config file
    update_value = {
        "share": {
            "max_dom": max_dom,
            "start_date": start_date,
            "end_date": end_date,
            "interval_seconds": interval_seconds
        },
        "geogrid": {
            "parent_grid_ratio": wrf_config["domain"]["parent_grid_ratio"],
            "i_parent_start": wrf_config["domain"]["i_parent_start"],
            "j_parent_start": wrf_config["domain"]["j_parent_start"],
            "e_we": wrf_config["domain"]["e_we"],
            "e_sn": wrf_config["domain"]["e_sn"],
            "dx": wrf_config["domain"]["dx"],
            "dy": wrf_config["domain"]["dy"],
            "ref_lat": wrf_config["domain"]["ref_lat"],
            "ref_lon": wrf_config["domain"]["ref_lon"],
            "map_proj": wrf_config["domain"]["map_proj"],
            "truelat1": wrf_config["domain"]["truelat1"],
            "truelat2": wrf_config["domain"]["truelat2"],
            "stand_lon": wrf_config["domain"]["stand_lon"],
            "geog_data_path": wrf_config["geog_data_path"]
        },
        "ungrib": {"prefix": f"{UNGRIB_OUTPUT_DIR}/FILE"},
        "metgrid": {"fg_name": f"{UNGRIB_OUTPUT_DIR}/FILE"}
    }

    # # update namelist
    WRFRUNConfig.update_namelist(update_value, "wps")

    # # update settings from custom namelist
    if wrf_config["user_wps_namelist"] != "" and exists(wrf_config["user_wps_namelist"]):
        WRFRUNConfig.update_namelist(wrf_config["user_wps_namelist"], "wps")


def prepare_wrf_namelist():
    """
    This function read WRF template namelist and update its value based on the config file and user custom namelist.

    """
    # read template namelist
    WRFRUNConfig.read_namelist(WRFRUNConfig.parse_resource_uri(NAMELIST_WRF), "wrf")

    # wrf config from config
    wrf_config = WRFRUNConfig.get_model_config("wrf")

    # get debug level
    debug_level = wrf_config["debug_level"]

    # get domain number, start_date and end_date
    max_dom = wrf_config["domain"]["domain_num"]
    start_date = wrf_config["time"]["start_date"]
    end_date = wrf_config["time"]["end_date"]
    
    start_date, end_date = _check_start_end_date(max_dom, start_date, end_date)

    # get the time interval of input data and output data
    input_data_interval = wrf_config["time"]["input_data_interval"]
    output_data_interval = wrf_config["time"]["output_data_interval"]

    # get restart settings
    restart = wrf_config["restart_mode"]
    restart_interval = wrf_config["time"]["restart_interval"]
    if restart_interval < 0:
        restart_interval = output_data_interval

    # get the time step of integral
    time_step = wrf_config["time"]["time_step"]

    # calculate run hours
    run_hours = end_date[0] - start_date[0]
    run_hours = run_hours.days * 24 + run_hours.seconds // 3600

    # calculate dx and dy for each domain
    dx = wrf_config["domain"]["dx"]
    dy = wrf_config["domain"]["dy"]
    parent_grid_ratio = wrf_config["domain"]["parent_grid_ratio"]
    dx = [dx // ratio for ratio in parent_grid_ratio]
    dy = [dy // ratio for ratio in parent_grid_ratio]

    # prepare update values
    update_values = {
        "time_control": {
            # make sure run days, minutes, and seconds are 0
            "run_days": 0,
            "run_minutes": 0,
            "run_seconds": 0,
            "run_hours": run_hours,
            "start_year": [_date.year for _date in start_date],
            "start_month": [_date.month for _date in start_date],
            "start_day": [_date.day for _date in start_date],
            "start_hour": [_date.hour for _date in start_date],
            "start_minute": [_date.minute for _date in start_date],
            "start_second": [_date.second for _date in start_date],
            "end_year": [_date.year for _date in end_date],
            "end_month": [_date.month for _date in end_date],
            "end_day": [_date.day for _date in end_date],
            "end_hour": [_date.hour for _date in end_date],
            "end_minute": [_date.minute for _date in end_date],
            "end_second": [_date.second for _date in end_date],
            "interval_seconds": input_data_interval,
            "history_interval": [output_data_interval for _ in range(max_dom)],
            "auxinput4_interval": [input_data_interval // 60 for _ in range(max_dom)],
            "restart": restart,
            "restart_interval": restart_interval,
            "debug_level": debug_level,
        },
        "domains": {
            "max_dom": max_dom,
            "time_step": time_step,
            "parent_grid_ratio": parent_grid_ratio,
            "i_parent_start": wrf_config["domain"]["i_parent_start"],
            "j_parent_start": wrf_config["domain"]["j_parent_start"],
            "e_we": wrf_config["domain"]["e_we"],
            "e_sn": wrf_config["domain"]["e_sn"],
            "dx": dx,
            "dy": dy,

        },
        "physics": {}
    }

    # and we need to check the physics scheme option
    long_wave_scheme = {
        "ra_lw_physics": [SchemeLongWave.get_scheme_id(wrf_config["scheme"]["long_wave_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    long_wave_scheme.update(wrf_config["scheme"]["long_wave_scheme"]["option"])
    # update
    update_values["physics"].update(long_wave_scheme)

    short_wave_scheme = {
        "ra_sw_physics": [SchemeShortWave.get_scheme_id(wrf_config["scheme"]["short_wave_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    short_wave_scheme.update(
        wrf_config["scheme"]["short_wave_scheme"]["option"])
    # update
    update_values["physics"].update(short_wave_scheme)

    cumulus_scheme = {
        "cu_physics": [SchemeCumulus.get_scheme_id(wrf_config["scheme"]["cumulus_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    cumulus_scheme.update(wrf_config["scheme"]["cumulus_scheme"]["option"])
    # update
    update_values["physics"].update(cumulus_scheme)

    pbl_scheme = {
        "bl_pbl_physics": [SchemePBL.get_scheme_id(wrf_config["scheme"]["pbl_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    pbl_scheme.update(wrf_config["scheme"]["pbl_scheme"]["option"])
    # update
    update_values["physics"].update(pbl_scheme)

    land_surface_scheme = {
        "sf_surface_physics": [SchemeLandSurfaceModel.get_scheme_id(wrf_config["scheme"]["land_surface_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    land_surface_scheme.update(
        wrf_config["scheme"]["land_surface_scheme"]["option"])
    # update
    update_values["physics"].update(land_surface_scheme)

    surface_layer_scheme = {
        "sf_sfclay_physics": [SchemeSurfaceLayer.get_scheme_id(wrf_config["scheme"]["surface_layer_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    surface_layer_scheme.update(
        wrf_config["scheme"]["surface_layer_scheme"]["option"])
    # update
    update_values["physics"].update(surface_layer_scheme)

    # update namelist
    WRFRUNConfig.update_namelist(update_values, "wrf")

    # read user real namelist and update value
    user_namelist_data = wrf_config["user_wrf_namelist"]
    if user_namelist_data != "" and exists(user_namelist_data):
        WRFRUNConfig.update_namelist(user_namelist_data, "wrf")


def prepare_dfi_namelist():
    """Generate namelist data for DFI running

    """
    # Read template namelist
    WRFRUNConfig.read_namelist(WRFRUNConfig.parse_resource_uri(NAMELIST_DFI), "dfi")

    wrf_config = WRFRUNConfig.get_model_config("wrf")

    # Read start date and end date
    start_date = wrf_config["time"]["start_date"]
    start_date = start_date[0] if isinstance(start_date, list) else start_date
    input_data_interval = wrf_config["time"]["input_data_interval"]
    time_step = wrf_config["time"]["time_step"]
    # calculate dfi date because:
    # dfi start date is 1 hour earlier than start_date
    # dfi end date is 30 minutes later than start_date
    dfi_start_date = start_date - timedelta(hours=1)
    dfi_end_date = start_date + timedelta(minutes=30)

    # calculate dx and dy for each domain
    dx = wrf_config["domain"]["dx"]
    dy = wrf_config["domain"]["dy"]
    parent_grid_ratio = wrf_config["domain"]["parent_grid_ratio"]
    dx = [dx // ratio for ratio in parent_grid_ratio]
    dy = [dy // ratio for ratio in parent_grid_ratio]

    # Construct update value
    update_value = {
        "time_control": {
            # make sure run days, hours, minutes, seconds is 0
            "run_days": 0,
            "run_hours": 0,
            "run_minutes": 0,
            "run_seconds": 0,
            # start date and end date are same
            "start_year": [start_date.year],
            "start_month": [start_date.month],
            "start_day": [start_date.day],
            "start_hour": [start_date.hour],
            "start_minute": [start_date.minute],
            "start_second": [start_date.second],
            "end_year": [start_date.year],
            "end_month": [start_date.month],
            "end_day": [start_date.day],
            "end_hour": [start_date.hour],
            "end_minute": [start_date.minute],
            "end_second": [start_date.second],
            "interval_seconds": input_data_interval,
            "auxinput4_interval_s": [input_data_interval, ]
        },
        "domains": {
            # make sure max_dom = 1
            "time_step": time_step,
            "max_dom": 1,
            "time_step_dfi": time_step if time_step < 90 else 90,
            "parent_grid_ratio": parent_grid_ratio,
            "i_parent_start": wrf_config["domain"]["i_parent_start"],
            "j_parent_start": wrf_config["domain"]["j_parent_start"],
            "e_we": wrf_config["domain"]["e_we"],
            "e_sn": wrf_config["domain"]["e_sn"],
            "dx": dx,
            "dy": dy,
        },
        "dfi_control": {
            # set dfi date
            "dfi_bckstop_year": dfi_start_date.year,
            "dfi_bckstop_month": dfi_start_date.month,
            "dfi_bckstop_day": dfi_start_date.day,
            "dfi_bckstop_hour": dfi_start_date.hour,
            "dfi_bckstop_minute": dfi_start_date.minute,
            "dfi_bckstop_second": dfi_start_date.second,
            "dfi_fwdstop_year": dfi_end_date.year,
            "dfi_fwdstop_month": dfi_end_date.month,
            "dfi_fwdstop_day": dfi_end_date.day,
            "dfi_fwdstop_hour": dfi_end_date.hour,
            "dfi_fwdstop_minute": dfi_end_date.minute,
            "dfi_fwdstop_second": dfi_end_date.second,
        }
    }

    # update namelist data
    WRFRUNConfig.update_namelist(update_value, "dfi")

    # read user wrf namelist and update value
    user_namelist_data = wrf_config["user_wrf_namelist"]
    if user_namelist_data != "" and exists(user_namelist_data):
        WRFRUNConfig.update_namelist(user_namelist_data, "dfi")


def prepare_wrfda_namelist():
    """Generate namelist for da_wrfvar.exe

    """
    # read template namelist
    WRFRUNConfig.read_namelist(WRFRUNConfig.parse_resource_uri(NAMELIST_WRFDA), "wrfda")

    wrf_config = WRFRUNConfig.get_model_config("wrf")

    # get wrf start date
    start_date = wrf_config["time"]["start_date"]
    start_date = start_date[0] if isinstance(start_date, list) else start_date

    # generate update value
    update_value = {
        "wrfvar18": {
            "analysis_date": start_date.strftime("%Y-%m-%d_%H:%M:%S.0000")
        },
        "wrfvar21": {
            # one hour before wrf start date
            "time_window_min": (start_date - timedelta(hours=1)).strftime("%Y-%m-%d_%H:%M:%S.0000")
        },
        "wrfvar22": {
            # one hour after wrf start date
            "time_window_max": (start_date + timedelta(hours=1)).strftime("%Y-%m-%d_%H:%M:%S.0000")
        }
    }

    # update namelist
    WRFRUNConfig.update_namelist(update_value, "wrfda")

    # read user wrfda namelist and update value
    user_namelist_data = wrf_config["user_wrfda_namelist"]
    if user_namelist_data != "" and exists(user_namelist_data):
        WRFRUNConfig.update_namelist(user_namelist_data, "wrfda")


__all__ = ["prepare_wrf_namelist", "prepare_wps_namelist", "prepare_wrfda_namelist", "prepare_dfi_namelist", "get_ungrib_out_prefix", "get_ungrib_out_dir_path",
           "set_ungrib_out_prefix", "get_metgrid_fg_names", "set_metgrid_fg_names"]
