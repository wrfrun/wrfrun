"""Shared ARPS namelist preparation helpers."""

import logging
from datetime import datetime

from wrfrun.core import WRFRUN_NEW

from ...namelist import get_project_namelist_files

LOGGER = logging.getLogger("wrfrun")

PROJECTION_MAP = {
    "polar_north": 1,
    "polar_south": -1,
    "lambert_north": 2,
    "lambert_south": -2,
    "mercator": 3,
    "": 0,
}


def load_component_namelist(component: str, filename: str) -> None:
    """Load one executable's namelist template into its own namelist ID."""
    if not WRFRUN_NEW.namelist.check_namelist_id(component):
        WRFRUN_NEW.namelist.register_namelist_id(component)

    template_file, _ = get_project_namelist_files("arps", component, filename)
    WRFRUN_NEW.namelist.read_namelist(template_file.as_posix(), component)


def apply_component_namelist_updates(component: str, filename: str) -> None:
    """Apply user and experiment namelist updates for one executable."""
    _, update_files = get_project_namelist_files("arps", component, filename)
    for update_file in update_files:
        if update_file.is_file():
            WRFRUN_NEW.namelist.update_namelist(update_file.as_posix(), component)


def prepare_component_namelist(component: str, filename: str | None = None) -> None:
    """Load a component template and apply its project updates."""
    filename = filename or f"{component}.nml"
    load_component_namelist(component, filename)
    apply_component_namelist_updates(component, filename)


def prepare_arps_namelist(component: str) -> None:
    """Prepare the ARPS-format namelist used by one executable component."""
    model_config = WRFRUN_NEW.config.get_model_config("arps")
    load_component_namelist(component, f"{component}.nml")

    grid_projection = model_config["global"]["grid_projection"]
    grid_center_latitude = model_config["global"]["grid_center_latitude"]
    if grid_projection in ("polar", "lambert"):
        grid_projection = f"{grid_projection}_north" if grid_center_latitude >= 0 else f"{grid_projection}_south"

    start_date: datetime = WRFRUN_NEW.config["simulation"]["time"]["start_time"]
    end_date: datetime = WRFRUN_NEW.config["simulation"]["time"]["end_time"]
    WRFRUN_NEW.namelist.update_namelist(
        {
            "grid_dims": {
                "nx": model_config["global"]["grid_nx"],
                "ny": model_config["global"]["grid_ny"],
                "nz": model_config["global"]["grid_nz"],
            },
            "jobname": {"runname": "wrfrun"},
            "initialization": {"initime": start_date.strftime("%Y-%m-%d.%H:%M:%S")},
            "grid": {
                "dx": model_config["global"]["grid_dx"],
                "dy": model_config["global"]["grid_dy"],
                "dz": model_config["global"]["grid_dz"],
                "dzmin": model_config["global"]["grid_min_dz"],
                "zrefsfc": model_config["global"]["grid_z_bottom_height"],
                "dlayer1": model_config["global"]["grid_z_stretch_start_height"],
                "dlayer2": model_config["global"]["grid_z_stretch_end_height"],
                "zflat": model_config["global"]["grid_z_start_flat_height"],
                "ctrlat": grid_center_latitude,
                "ctrlon": model_config["global"]["grid_center_longitude"],
            },
            "projection": {
                "mapproj": PROJECTION_MAP[grid_projection],
                "trulat1": model_config["global"]["grid_projection_true_lat_1"],
                "trulat2": model_config["global"]["grid_projection_true_lat_2"],
                "trulon": model_config["global"]["grid_projection_true_lon"],
            },
            "soil_veg_data": {
                "fgendi": model_config["global"]["grid_nx"],
                "fgendj": model_config["global"]["grid_ny"],
            },
            "timestep": {
                "dtbig": model_config["global"]["integrate_large_time_step"],
                "tstop": int((end_date - start_date).total_seconds()),
            },
            "output": {"dirname": "./outputs/"},
        },
        component,
    )
    apply_component_namelist_updates(component, f"{component}.nml")

    if WRFRUN_NEW.namelist.get_namelist(component)["initialization"].get("inisplited", -1) != 0:
        message = (
            "It is recommended to let arps core read input data and split it on-the-fly. "
            "Set inisplited=0 in 'initialization' block to fix this error."
        )
        LOGGER.error(message)
        raise ValueError(message)


__all__ = ["prepare_arps_namelist", "prepare_component_namelist"]
