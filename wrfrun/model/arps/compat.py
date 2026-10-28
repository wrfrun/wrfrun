"""
Compat layer of ARPS.

This module may be removed at ANY time.
"""

import logging
from pathlib import Path
from shutil import copyfile

from wrfrun.core import WRFRUN_NEW

LOGGER = logging.getLogger("wrfrun")
LOGGER.warning("You are using 'wrfrun.model.arps.compat' which may be removed at [magenta]ANY[/magenta] time, be careful.")


def copy_arps_namelist_template():
    """
    Copy namelist needed conveniently.
    """
    ARPS_MODEL_CONFIG = WRFRUN_NEW.config.get_model_config("arps")
    ARPS_BIN_DIR = Path(ARPS_MODEL_CONFIG["global"]["arps_bin_directory"]).resolve()
    ARPS_INPUT_DIR = ARPS_BIN_DIR.parent / "input"
    submodel_name_list = [x for x in ARPS_MODEL_CONFIG if x not in ("global", "use")]

    for _submodel in submodel_name_list:
        match _submodel:
            case "arps" | "arpssfc" | "ext2arps" | "arps3dvar":
                namelist_name = "arps.input"
                component = _submodel

            case "arpstrn":
                namelist_name = "arpstrn.input"
                component = "arpstrn"

            case "arpsintrp":
                namelist_name = "arpsintrp.input"
                component = "arpsintrp"

            case "radremap":
                namelist_name = "radremap.input"
                component = "radremap"

            case _:
                continue

        target = WRFRUN_NEW.resource.get_custom_resource(
            WRFRUN_NEW.resource.NAMELIST_TEMPLATE_DIR / "arps" / component / Path(namelist_name).with_suffix(".nml").name
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Copy '{ARPS_INPUT_DIR / namelist_name}' to '{target}'")
        copyfile(ARPS_INPUT_DIR / namelist_name, target)


__all__ = ["copy_arps_namelist_template"]
