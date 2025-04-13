from dataclasses import dataclass
from typing import Optional

from ..core import ExecutableBase, LoadConfigError, WRFRUNConfig
from ..utils import logger


@dataclass
class NamelistName:
    """
    Namelist file names.
    """
    WPS = "namelist.wps"
    WRF = "namelist.input"
    WRFDA = "namelist.input"


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
        save_path = f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}"
    elif namelist_type == "wrf":
        save_path = f"{WRFRUNConfig.WRF_WORK_PATH}/{NamelistName.WRF}"
    elif namelist_type == "wrfda":
        save_path = f"{WRFRUNConfig.WRFDA_WORK_PATH}/{NamelistName.WRFDA}"
    else:
        if save_path is None:
            logger.error(f"`save_path` is needed to save custom namelist.")
            raise ValueError(f"`save_path` is needed to save custom namelist.")

    WRFRUNConfig.namelist.write_namelist(save_path, namelist_type)


__all__ = ["NamelistName"]
