from wrfrun.core import WRFRUNConfig, WRFRUNNamelist
from wrfrun.utils import logger


def process_after_ndown():
    """
    After running ndown.exe, namelist settings are supposed to be changed,
    so WRF can simulate a higher resolution domain according to `WRF User's Guide <https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/running_wrf.html#wrf-nesting>`_.
    `wrfrun` provide this function to help you change these settings which have multiple values for each domain.
    The first value will be removed to ensure the value of higher resolution domain is the first value.

    :return:
    """
    namelist_data = WRFRUNNamelist.get_namelist("wrf")

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

    time_ratio = WRFRUNConfig.get_wrf_config()["time"]["parent_time_step_ratio"][1]
    namelist_data["domains"]["time_step"] = namelist_data["domains"]["time_step"] // time_ratio

    WRFRUNNamelist.update_namelist(namelist_data, "wrf")

    logger.info(f"Update namelist after running ndown.exe")


__all__ = ["process_after_ndown"]
