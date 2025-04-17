from dataclasses import dataclass


@dataclass
class NamelistName:
    """
    Namelist file names.
    """
    WPS = "namelist.wps"
    WRF = "namelist.input"
    WRFDA = "namelist.input"


__all__ = ["NamelistName"]
