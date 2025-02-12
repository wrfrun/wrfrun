from datetime import datetime, timedelta
from os.path import exists
from typing import Optional

from wrfrun.core import WRFRUNConfig, WRFRUNConstants, WRFRUNNamelist
from wrfrun.res import NAMELIST_DA_WRFVAR_TEMPLATE, NAMELIST_DFI_TEMPLATE, NAMELIST_WPS_TEMPLATE, NAMELIST_WRF_TEMPLATE
from wrfrun.utils import logger
from .scheme import get_cumulus_scheme, get_land_surface_scheme, get_long_wave_scheme, get_pbl_scheme, get_short_wave_scheme, get_surface_layer_scheme


def generate_namelist_file(namelist_type: str, save_path: Optional[str] = None):
    """
    Write namelist to a file so WPS or WRF can use its settings.

    :param namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type registered.
    :type namelist_type: str
    :param save_path: If namelist_type isn't in ``["wps", "wrf", "wrfda"]``, ``save_path`` must be specified.
    :type save_path: str | None
    :return:
    """
    if namelist_type == "wps":
        save_path = f"{WRFRUNConstants.get_work_path(namelist_type)}/namelist.wps"
    elif namelist_type == "wrf":
        save_path = f"{WRFRUNConstants.get_work_path(namelist_type)}/namelist.input"
    elif namelist_type == "wrfda":
        save_path = f"{WRFRUNConstants.get_work_path(namelist_type)}/namelist.input"
    else:
        if save_path is None:
            logger.error(f"`save_path` is needed to save custom namelist.")
            raise ValueError(f"`save_path` is needed to save custom namelist.")

    WRFRUNNamelist.write_namelist(save_path, namelist_type)


def prepare_wps_namelist():
    """
    This function read WPS template namelist and update its value based on the config file and user custom namelist.

    """
    # prepare namelist
    # # read template
    WRFRUNNamelist.read_namelist(NAMELIST_WPS_TEMPLATE, "wps")

    # # get wrf config from config
    wrf_config = WRFRUNConfig.get_wrf_config()

    # # get domain number
    max_dom = wrf_config["domain"]["domain_num"]

    # # get start_date and end_date
    start_date = datetime.strptime(
        wrf_config["time"]["start_date"], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(
        wrf_config["time"]["end_date"], "%Y-%m-%d %H:%M:%S")

    # # get input data time interval
    interval_seconds = wrf_config["time"]["input_data_interval"]

    # # generate update settings based on the config file
    update_value = {
        "share": {
            "max_dom": max_dom,
            "start_date": [
                start_date.strftime("%Y-%m-%d_%H:%M:%S") for _ in range(max_dom)
            ],
            "end_date": [
                end_date.strftime("%Y-%m-%d_%H:%M:%S") for _ in range(max_dom)
            ],
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
            "stand_lon": wrf_config["domain"]["stand_lon"],
            "geog_data_path": wrf_config["geog_data_path"]
        }
    }

    # # use loop to process config of map_proj
    for key in wrf_config["domain"]["map_proj"]:
        if key == "name":
            update_value["geogrid"]["map_proj"] = wrf_config["domain"]["map_proj"][key]
        else:
            update_value["geogrid"][key] = wrf_config["domain"]["map_proj"][key]

    # # update namelist
    WRFRUNNamelist.update_namelist(update_value, "wps")

    # # update settings from custom namelist
    if wrf_config["user_wps_namelist"] != "" and exists(wrf_config["user_wps_namelist"]):
        WRFRUNNamelist.update_namelist(wrf_config["user_wps_namelist"], "wps")


def prepare_wrf_namelist():
    """
    This function read WRF template namelist and update its value based on the config file and user custom namelist.

    """
    # read template namelist
    WRFRUNNamelist.read_namelist(NAMELIST_WRF_TEMPLATE, "wrf")

    # wrf config from config
    wrf_config = WRFRUNConfig.get_wrf_config()

    # get debug level
    debug_level = wrf_config["debug_level"]

    # get domain number, start_date and end_date
    max_dom = wrf_config["domain"]["domain_num"]
    start_date = datetime.strptime(
        wrf_config["time"]["start_date"], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(
        wrf_config["time"]["end_date"], "%Y-%m-%d %H:%M:%S")

    # get time interval of input data and output data
    input_data_interval = wrf_config["time"]["input_data_interval"]
    output_data_interval = wrf_config["time"]["output_data_interval"]

    # get restart interval
    restart_interval = wrf_config["time"]["restart_interval"]
    if restart_interval < 0:
        restart_interval = output_data_interval

    # get time step of integral
    time_step = wrf_config["time"]["time_step"]

    # calculate run hours
    run_hours = end_date - start_date
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
            "start_year": [start_date.year for _ in range(max_dom)],
            "start_month": [start_date.month for _ in range(max_dom)],
            "start_day": [start_date.day for _ in range(max_dom)],
            "start_hour": [start_date.hour for _ in range(max_dom)],
            "start_minute": [start_date.minute for _ in range(max_dom)],
            "start_second": [start_date.second for _ in range(max_dom)],
            "end_year": [end_date.year for _ in range(max_dom)],
            "end_month": [end_date.month for _ in range(max_dom)],
            "end_day": [end_date.day for _ in range(max_dom)],
            "end_hour": [end_date.hour for _ in range(max_dom)],
            "end_minute": [end_date.minute for _ in range(max_dom)],
            "end_second": [end_date.second for _ in range(max_dom)],
            "interval_seconds": input_data_interval,
            "history_interval": [output_data_interval for _ in range(max_dom)],
            "auxinput4_interval": [input_data_interval // 60 for _ in range(max_dom)],
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

    # and we need to check physics scheme option
    long_wave_scheme = {
        "ra_lw_physics": [get_long_wave_scheme(wrf_config["scheme"]["long_wave_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    long_wave_scheme.update(wrf_config["scheme"]["long_wave_scheme"]["option"])
    # update
    update_values["physics"].update(long_wave_scheme)

    short_wave_scheme = {
        "ra_sw_physics": [get_short_wave_scheme(wrf_config["scheme"]["short_wave_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    short_wave_scheme.update(
        wrf_config["scheme"]["short_wave_scheme"]["option"])
    # update
    update_values["physics"].update(short_wave_scheme)

    cumulus_scheme = {
        "cu_physics": [get_cumulus_scheme(wrf_config["scheme"]["cumulus_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    cumulus_scheme.update(wrf_config["scheme"]["cumulus_scheme"]["option"])
    # update
    update_values["physics"].update(cumulus_scheme)

    pbl_scheme = {
        "bl_pbl_physics": [get_pbl_scheme(wrf_config["scheme"]["pbl_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    pbl_scheme.update(wrf_config["scheme"]["pbl_scheme"]["option"])
    # update
    update_values["physics"].update(pbl_scheme)

    land_surface_scheme = {
        "sf_surface_physics": [get_land_surface_scheme(wrf_config["scheme"]["land_surface_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    land_surface_scheme.update(
        wrf_config["scheme"]["land_surface_scheme"]["option"])
    # update
    update_values["physics"].update(land_surface_scheme)

    surface_layer_scheme = {
        "sf_sfclay_physics": [get_surface_layer_scheme(wrf_config["scheme"]["surface_layer_scheme"]["name"]) for _ in range(max_dom)]
    }
    # # and other related options
    surface_layer_scheme.update(
        wrf_config["scheme"]["surface_layer_scheme"]["option"])
    # update
    update_values["physics"].update(surface_layer_scheme)

    # update namelist
    WRFRUNNamelist.update_namelist(update_values, "wrf")

    # read user real namelist and update value
    user_namelist_data = wrf_config["user_wrf_namelist"]
    if user_namelist_data != "" and exists(user_namelist_data):
        WRFRUNNamelist.update_namelist(user_namelist_data, "wrf")


def prepare_dfi_namelist():
    """Generate namelist data for DFI running

    """
    # Read template namelist
    WRFRUNNamelist.read_namelist(NAMELIST_DFI_TEMPLATE, "dfi")

    wrf_config = WRFRUNConfig.get_wrf_config()

    # Read start date and end date
    start_date = datetime.strptime(
        wrf_config["time"]["start_date"], "%Y-%m-%d %H:%M:%S")
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
            # start date and end date is same
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
    WRFRUNNamelist.update_namelist(update_value, "dfi")

    # read user wrf namelist and update value
    user_namelist_data = wrf_config["user_wrf_namelist"]
    if user_namelist_data != "" and exists(user_namelist_data):
        WRFRUNNamelist.update_namelist(user_namelist_data, "dfi")


def prepare_wrfda_namelist():
    """Generate namelist for da_wrfvar.exe

    """
    # read template namelist
    WRFRUNNamelist.read_namelist(NAMELIST_DA_WRFVAR_TEMPLATE, "wrfda")

    wrf_config = WRFRUNConfig.get_wrf_config()

    # get wrf start date
    start_date = datetime.strptime(wrf_config["time"]["start_date"], "%Y-%m-%d %H:%M:%S")

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
    WRFRUNNamelist.update_namelist(update_value, "wrfda")

    # read user wrfda namelist and update value
    user_namelist_data = wrf_config["user_wrfda_namelist"]
    if user_namelist_data != "" and exists(user_namelist_data):
        WRFRUNNamelist.update_namelist(user_namelist_data, "wrfda")


__all__ = ["prepare_wrf_namelist", "prepare_wps_namelist", "prepare_wrfda_namelist", "prepare_dfi_namelist", "generate_namelist_file"]
