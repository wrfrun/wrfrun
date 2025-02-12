"""
This file contains function to determine schemes for WRF
"""
from wrfrun.utils import logger


def get_long_wave_scheme(key: str = "rrtm"):
    """Get the corresponding integer label for long wave radiation scheme

    Args:
        key (str, optional): Name of long wave radiation scheme. Defaults to "rrtm".
    """
    # Here is the map of scheme name and integer label in WRF
    # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#longwave-radiation-schemes
    integer_label_map = {
        "off": 0,
        "rrtm": 1,
        "cam": 3,
        "rrtmg": 4,
        "new-goddard": 5,
        "flg": 7,
        "rrtmg-k": 14,
        "held-suarez": 31,
        "gfdl": 99
    }

    # check if key is in map
    if key not in integer_label_map:
        logger.error(
            f"Key error: {key}. Valid key: {list(integer_label_map.keys())}")
        raise KeyError

    return integer_label_map[key]


def get_short_wave_scheme(key: str = "rrtmg"):
    """Get corresponding integer label for short wave radiation scheme

    Args:
        key (str, optional): Name of short wave radiation scheme. Defaults to "rrtmg".
    """
    # Here is the map of scheme name and integer label in WRF
    # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#shortwave-radiation-schemes
    integer_label_map = {
        "off": 0,
        "dudhia": 1,
        "goddard": 2,
        "cam": 3,
        "rrtmg": 4,
        "new-goddard": 5,
        "flg": 7,
        "rrtmg-k": 14,
        "gfdl": 99
    }

    # check if key is in map
    if key not in integer_label_map:
        logger.error(
            f"Key error: {key}. Valid key: {list(integer_label_map.keys())}")
        raise KeyError

    return integer_label_map[key]


def get_cumulus_scheme(key: str = "kf"):
    """Get corresponding integer label for cumulus parameterization scheme

    Args:
        key (str, optional): Name of cumulus parameterization scheme. Defaults to "kf".
    """
    # Here is the map of scheme name and integer label in WRF
    # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#cumulus-parameterization
    integer_label_map = {
        "off": 0,
        "kf": 1,
        "bmj": 2,
        "gf": 3,
        "old-sas": 4,
        "grell-3": 5,
        "tiedtke": 6,
        "zmf": 7,
        "kf-cup": 10,
        "mkf": 11,
        "kiaps-sas": 14,
        "nt": 16,
        "gd": 93,
        "nsas": 96,
        "old-kf": 99
    }

    # check if key is in map
    if key not in integer_label_map:
        logger.error(
            f"Key error: {key}. Valid key: {list(integer_label_map.keys())}")
        raise KeyError

    return integer_label_map[key]


def get_pbl_scheme(key: str = "ysu"):
    """Get corresponding integer label for PBL scheme

    Args:
        key (str, optional): Name of PBL scheme. Defaults to "ysu".
    """
    # Here is the map of scheme name and integer label in WRF
    # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#pbl-scheme-options
    integer_label_map = {
        "off": 0,
        "ysu": 1,
        "myj": 2,
        "qe": 4,
        "mynn2": 5,
        "acm2": 7,
        "boulac": 8,
        "uw": 9,
        "temf": 10,
        "shin-hong": 11,
        "gbm": 12,
        "eeps": 16,
        "keps": 17,
        "mrf": 99
    }

    # check if key is in map
    if key not in integer_label_map:
        logger.error(
            f"Key error: {key}. Valid key: {list(integer_label_map.keys())}")
        raise KeyError

    return integer_label_map[key]


def get_land_surface_scheme(key: str = "noah"):
    """Get corresponding integer label for land surface scheme

    Args:
        key (str, optional): Name of land surface scheme. Defaults to "noah".
    """
    # Here is the map of scheme name and integer label in WRF
    # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#lsm-scheme-details-and-references
    integer_label_map = {
        "off": 0,
        "slab": 1,
        "noah": 2,
        "ruc": 3,
        "noah-mp": 4,
        "clm4": 5,
        "px": 7,
        "ssib": 8
    }

    # check if key is in map
    if key not in integer_label_map:
        logger.error(
            f"Key error: {key}. Valid key: {list(integer_label_map.keys())}")
        raise KeyError

    return integer_label_map[key]


def get_surface_layer_scheme(key: str = "mo"):
    """Get corresponding integer label for surface layer scheme

    Args:
        key (str, optional): Name of surface layer scheme. Defaults to "mo".
    """
    # Here is the map of scheme name and integer label in WRF
    # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/namelist_variables.html
    integer_label_map = {
        "off": 0,
        "mm5": 1,
        "mo": 2,
        "qnse": 4,
        "mynn": 5,
        "px": 7,
        "temf": 10,
        "old-mm5": 91
    }

    # check if key is in map
    if key not in integer_label_map:
        logger.error(
            f"Key error: {key}. Valid key: {list(integer_label_map.keys())}")
        raise KeyError

    return integer_label_map[key]


__all__ = ["get_long_wave_scheme", "get_short_wave_scheme", "get_cumulus_scheme", "get_pbl_scheme",
           "get_surface_layer_scheme", "get_land_surface_scheme"]
