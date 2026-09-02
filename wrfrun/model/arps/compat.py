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
            case "arps":
                namelist_name = "arps.input"

            case "arpssfc":
                namelist_name = "arps.input"

            case "arpstrn":
                namelist_name = "arpstrn.input"

            case "ext2arps":
                namelist_name = "arps.input"

            case _:
                namelist_name = "arps.input"

        target = Path("templates/arps") / namelist_name
        target = target.with_suffix(".nml")
        target.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Copy '{ARPS_INPUT_DIR / namelist_name}' to '{target}'")
        copyfile(ARPS_INPUT_DIR / namelist_name, target)


__all__ = ["copy_arps_namelist_template"]
