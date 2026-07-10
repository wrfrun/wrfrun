"""
wrfrun.model.arps.namelist
##########################

Functions to read and change ARPS namelist.

.. autosummary::
    :toctree: generated/


"""

import logging
from datetime import datetime

from wrfrun.core import WRFRUN

PROJECTION_MAP = {
    "polar_north": 1,
    "polar_south": -1,
    "lambert_north": 2,
    "lambert_south": -2,
    "mercator": 3,
    "": 0,
}
LOGGER = logging.getLogger("wrfrun")


def prepare_arps_namelist():
    """
    This function read ARPS namelist and update its value based on the config.
    """
    global PROJECTION_MAP
    wrfrun_config = WRFRUN.config

    model_config = wrfrun_config.get_model_config("arps")
    user_namelist = model_config["user_namelist"]
    run_name = "wrfrun"

    wrfrun_config.read_namelist(user_namelist, "arps")

    if wrfrun_config.get_namelist("arps")["initialization"].get("inisplited", -1) != 0:
        LOGGER.error(
            "It is recommended to let arps core read input data and split it on-the-fly. "
            "Set [magenta]inisplited=0[/magenta] in 'initialization' block to fix this error."
        )
        raise ValueError(
            "It is recommended to let arps core read input data and split it on-the-fly. "
            "Set inisplited=0 in 'initialization' block to fix this error."
        )

    # User's namelist has the highest priority.
    return

    # Update namelist
    # Grid settings
    grid_nx = model_config["grid_nx"]
    grid_dx = model_config["grid_dx"]
    grid_ny = model_config["grid_ny"]
    grid_dy = model_config["grid_dy"]
    grid_nz = model_config["grid_nz"]
    grid_dz = model_config["grid_dz"]
    grid_center_latitude = model_config["grid_center_latitude"]
    grid_center_longitude = model_config["grid_center_longitude"]
    grid_min_dz = model_config["grid_min_dz"]
    grid_z_bottom_height = model_config["grid_z_bottom_height"]
    grid_z_stretch_start_height = model_config["grid_z_stretch_start_height"]
    grid_z_stretch_end_height = model_config["grid_z_stretch_end_height"]
    grid_z_start_flat_height = model_config["grid_z_start_flat_height"]
    grid_projection = model_config["grid_projection"]
    grid_projection_true_lat_1 = model_config["grid_projection_true_lat_1"]
    grid_projection_true_lat_2 = model_config["grid_projection_true_lat_2"]
    grid_projection_true_lon = model_config["grid_projection_true_lon"]

    if grid_projection in ("polar", "lambert"):
        grid_projection = f"{grid_projection}_north" if grid_center_latitude >= 0 else f"{grid_projection}_south"

    grid_projection_num = PROJECTION_MAP[grid_projection]

    # Integrate settings.
    integrate_large_time_step = model_config["integrate_large_time_step"]
    start_date: datetime = wrfrun_config["simulation"]["time"]["start_time"]
    end_date: datetime = wrfrun_config["simulation"]["time"]["end_time"]
    simulation_time = (end_date - start_date).seconds

    update_value = {
        "grid_dims": {"nx": grid_nx, "ny": grid_ny, "nz": grid_nz},
        "jobname": {"runname": run_name},
        "initialization": {
            "initime": start_date.strftime("%Y-%m-%d.%H:%M:%S"),
            "initopt": 2 if model_config["is_restart"] else 3,
        },
        "grid": {
            "dx": grid_dx,
            "dy": grid_dy,
            "dz": grid_dz,
            "strhopt": 2,
            "dzmin": grid_min_dz,
            "zrefsfc": grid_z_bottom_height,
            "dlayer1": grid_z_stretch_start_height,
            "dlayer2": grid_z_stretch_end_height,
            "zflat": grid_z_start_flat_height,
            "ctrlat": grid_center_latitude,
            "ctrlon": grid_center_longitude,
        },
        "projection": {
            "mapproj": grid_projection_num,
            "trulat1": grid_projection_true_lat_1,
            "trulat2": grid_projection_true_lat_2,
            "trulon": grid_projection_true_lon,
        },
        "timestep": {"dtbig": integrate_large_time_step, "tstop": simulation_time},
        "output": {"dirname": "./outputs/"},
    }
    wrfrun_config.update_namelist(update_value, "arps")


__all__ = ["prepare_arps_namelist"]
