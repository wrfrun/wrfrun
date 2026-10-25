"""
wrfrun.model.arps.namelist
##########################

Functions to read and change ARPS namelist.

.. autosummary::
    :toctree: generated/

    prepare_arps_namelist
    prepare_arpsintrp_namelist
    prepare_radremap_namelist
"""

import logging
from datetime import datetime

from wrfrun.core import WRFRUN_NEW

from ..namelist import get_project_namelist_files

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
    model_config = WRFRUN_NEW.config.get_model_config("arps")

    template_file, update_files = get_project_namelist_files("arps", "arps", "arps.nml")
    WRFRUN_NEW.namelist.read_namelist(template_file.as_posix(), "arps")

    run_name = "wrfrun"

    # Update namelist
    # Grid settings
    grid_nx = model_config["global"]["grid_nx"]
    grid_dx = model_config["global"]["grid_dx"]
    grid_ny = model_config["global"]["grid_ny"]
    grid_dy = model_config["global"]["grid_dy"]
    grid_nz = model_config["global"]["grid_nz"]
    grid_dz = model_config["global"]["grid_dz"]
    grid_center_latitude = model_config["global"]["grid_center_latitude"]
    grid_center_longitude = model_config["global"]["grid_center_longitude"]
    grid_min_dz = model_config["global"]["grid_min_dz"]
    grid_z_bottom_height = model_config["global"]["grid_z_bottom_height"]
    grid_z_stretch_start_height = model_config["global"]["grid_z_stretch_start_height"]
    grid_z_stretch_end_height = model_config["global"]["grid_z_stretch_end_height"]
    grid_z_start_flat_height = model_config["global"]["grid_z_start_flat_height"]
    grid_projection = model_config["global"]["grid_projection"]
    grid_projection_true_lat_1 = model_config["global"]["grid_projection_true_lat_1"]
    grid_projection_true_lat_2 = model_config["global"]["grid_projection_true_lat_2"]
    grid_projection_true_lon = model_config["global"]["grid_projection_true_lon"]

    if grid_projection in ("polar", "lambert"):
        grid_projection = f"{grid_projection}_north" if grid_center_latitude >= 0 else f"{grid_projection}_south"

    grid_projection_num = PROJECTION_MAP[grid_projection]

    # Integrate settings.
    integrate_large_time_step = model_config["global"]["integrate_large_time_step"]
    start_date: datetime = WRFRUN_NEW.config["simulation"]["time"]["start_time"]
    end_date: datetime = WRFRUN_NEW.config["simulation"]["time"]["end_time"]
    simulation_time = int((end_date - start_date).total_seconds())

    update_value = {
        "grid_dims": {"nx": grid_nx, "ny": grid_ny, "nz": grid_nz},
        "jobname": {"runname": run_name},
        "initialization": {
            "initime": start_date.strftime("%Y-%m-%d.%H:%M:%S"),
        },
        "grid": {
            "dx": grid_dx,
            "dy": grid_dy,
            "dz": grid_dz,
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
        "soil_veg_data": {
            "fgendi": grid_nx,
            "fgendj": grid_ny,
        },
        "timestep": {"dtbig": integrate_large_time_step, "tstop": simulation_time},
        "output": {"dirname": "./outputs/"},
    }
    WRFRUN_NEW.namelist.update_namelist(update_value, "arps")

    for update_file in update_files:
        if update_file.is_file():
            WRFRUN_NEW.namelist.update_namelist(update_file.as_posix(), "arps")

    if WRFRUN_NEW.namelist.get_namelist("arps")["initialization"].get("inisplited", -1) != 0:
        LOGGER.error(
            "It is recommended to let arps core read input data and split it on-the-fly. "
            "Set [magenta]inisplited=0[/magenta] in 'initialization' block to fix this error."
        )
        raise ValueError(
            "It is recommended to let arps core read input data and split it on-the-fly. "
            "Set inisplited=0 in 'initialization' block to fix this error."
        )

    return


def _prepare_component_namelist(namelist_id: str):
    """Load an ARPS component namelist template and its optional updates."""
    template_file, update_files = get_project_namelist_files("arps", namelist_id, f"{namelist_id}.nml")

    if not WRFRUN_NEW.namelist.check_namelist_id(namelist_id):
        WRFRUN_NEW.namelist.register_namelist_id(namelist_id)

    WRFRUN_NEW.namelist.read_namelist(template_file.as_posix(), namelist_id)
    for update_file in update_files:
        if update_file.is_file():
            WRFRUN_NEW.namelist.update_namelist(update_file.as_posix(), namelist_id)


def prepare_arpsintrp_namelist():
    """Load the project ``arpsintrp`` template and optional updates."""
    _prepare_component_namelist("arpsintrp")


def prepare_radremap_namelist():
    """Load the project ``radremap`` template and optional updates."""
    _prepare_component_namelist("radremap")


__all__ = ["prepare_arps_namelist", "prepare_arpsintrp_namelist", "prepare_radremap_namelist"]
