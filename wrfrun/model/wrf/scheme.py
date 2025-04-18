"""
This file contains function to determine schemes for WRF
"""
from dataclasses import dataclass

from wrfrun.utils import logger


@dataclass()
class SchemeLongWave:
    """
    Long wave physics schemes.
    """
    OFF = 0
    RRTM = 1
    CAM = 3
    RRTMG = 4
    NEW_GODDARD = 5
    FLG = 7
    RRTMG_K = 14
    FAST_RRTMG = 24     # for GPU and MIC
    HELD_SUAREZ = 31
    GFDL = 99

    @classmethod
    def get_scheme_id(cls, key: str = "rrtm"):
        """Get the corresponding integer label for long wave radiation scheme

        Args:
            key (str, optional): Name of long wave radiation scheme. Defaults to "rrtm".
        """
        # Here is the map of scheme name and integer label in WRF
        # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#longwave-radiation-schemes
        integer_label_map = {
            "off": cls.OFF,
            "rrtm": cls.RRTM,
            "cam": cls.CAM,
            "rrtmg": cls.RRTMG,
            "new-goddard": cls.NEW_GODDARD,
            "flg": cls.FLG,
            "rrtmg-k": cls.RRTMG_K,
            "fast-rrtmg": cls.FAST_RRTMG,
            "held-suarez": cls.HELD_SUAREZ,
            "gfdl": cls.GFDL
        }

        # check if key is in map
        if key not in integer_label_map:
            logger.error(
                f"Key error: {key}. Valid key: {list(integer_label_map.keys())}"
            )
            raise KeyError

        return integer_label_map[key]


@dataclass()
class SchemeShortWave:
    """
    Short wave physics schemes.
    """
    OFF = 0
    DUDHIA = 1
    GODDARD = 2
    CAM = 3
    RRTMG = 4
    NEW_GODDARD = 5
    FLG = 7
    RRTMG_K = 14
    FAST_RRTMG = 24
    EARTH_HELD_SUAREZ_FORCING = 31
    GFDL = 99

    @classmethod
    def get_scheme_id(cls, key: str = "rrtmg"):
        """Get corresponding integer label for short wave radiation scheme

        Args:
            key (str, optional): Name of short wave radiation scheme. Defaults to "rrtmg".
        """
        # Here is the map of scheme name and integer label in WRF
        # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#shortwave-radiation-schemes
        integer_label_map = {
            "off": cls.OFF,
            "dudhia": cls.DUDHIA,
            "goddard": cls.GODDARD,
            "cam": cls.CAM,
            "rrtmg": cls.RRTMG,
            "new-goddard": cls.NEW_GODDARD,
            "flg": cls.FLG,
            "rrtmg-k": cls.RRTMG_K,
            "fast-rrtmg": cls.FAST_RRTMG,
            "earth-hs-force": cls.EARTH_HELD_SUAREZ_FORCING,
            "gfdl": cls.GODDARD
        }

        # check if key is in map
        if key not in integer_label_map:
            logger.error(
                f"Key error: {key}. Valid key: {list(integer_label_map.keys())}"
            )
            raise KeyError

        return integer_label_map[key]


@dataclass()
class SchemeCumulus:
    """
    Cumulus parameterization schemes.
    """
    OFF = 0
    KAIN_FRITSCH = 1
    BMJ = 2
    GRELL_FREITAS = 3
    OLD_SAS = 4
    GRELL_3 = 5
    TIEDTKE = 6
    ZHANG_MCFARLANE = 7
    KF_CUP = 10
    MULTI_SCALE_KF = 11
    KIAPS_SAS = 14
    NEW_TIEDTKE = 16
    GRELL_DEVENYI = 93
    NSAS = 96
    OLD_KF = 99

    @classmethod
    def get_scheme_id(cls, key: str = "kf"):
        """Get corresponding integer label for cumulus parameterization scheme

        Args:
            key (str, optional): Name of cumulus parameterization scheme. Defaults to "kf".
        """
        # Here is the map of scheme name and integer label in WRF
        # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#cumulus-parameterization
        integer_label_map = {
            "off": cls.OFF,
            "kf": cls.KAIN_FRITSCH,
            "bmj": cls.BMJ,
            "gf": cls.GRELL_FREITAS,
            "old-sas": cls.OLD_SAS,
            "grell-3": cls.GRELL_3,
            "tiedtke": cls.TIEDTKE,
            "zmf": cls.ZHANG_MCFARLANE,
            "kf-cup": cls.KF_CUP,
            "mkf": cls.MULTI_SCALE_KF,
            "kiaps-sas": cls.KIAPS_SAS,
            "nt": cls.NEW_TIEDTKE,
            "gd": cls.GRELL_DEVENYI,
            "nsas": cls.NSAS,
            "old-kf": cls.OLD_KF
        }

        # check if key is in map
        if key not in integer_label_map:
            logger.error(
                f"Key error: {key}. Valid key: {list(integer_label_map.keys())}"
            )
            raise KeyError

        return integer_label_map[key]


@dataclass()
class SchemePBL:
    """
    PBL physics schemes.
    """
    OFF = 0
    YSU = 1
    MYJ = 2
    QNSE_EDMF = 4
    MYNN2 = 5
    MYNN3 = 6
    ACM2 = 7
    BOULAC = 8
    UW = 9
    TEMF = 10
    SHIN_HONG = 11
    GBM = 12
    EEPS = 16
    KEPS = 17
    MRF = 99

    @classmethod
    def get_scheme_id(cls, key: str = "ysu"):
        """Get corresponding integer label for PBL scheme

        Args:
            key (str, optional): Name of PBL scheme. Defaults to "ysu".
        """
        # Here is the map of scheme name and integer label in WRF
        # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#pbl-scheme-options
        integer_label_map = {
            "off": cls.OFF,
            "ysu": cls.YSU,
            "myj": cls.MYJ,
            "qe": cls.QNSE_EDMF,
            "mynn2": cls.MYNN2,
            "mynn3": cls.MYNN3,
            "acm2": cls.ACM2,
            "boulac": cls.BOULAC,
            "uw": cls.UW,
            "temf": cls.TEMF,
            "shin-hong": cls.SHIN_HONG,
            "gbm": cls.GBM,
            "eeps": cls.EEPS,
            "keps": cls.KEPS,
            "mrf": cls.MRF
        }

        # check if key is in map
        if key not in integer_label_map:
            logger.error(
                f"Key error: {key}. Valid key: {list(integer_label_map.keys())}"
            )
            raise KeyError

        return integer_label_map[key]


@dataclass()
class SchemeLandSurfaceModel:
    """
    Land surface model physics schemes.
    """
    OFF = 0
    SLAB = 1
    NOAH = 2
    RUC = 3
    NOAH_MP = 4
    CLM4 = 5
    PLEIM_XIU = 7
    SSIB = 8

    @classmethod
    def get_scheme_id(cls, key: str = "noah"):
        """Get corresponding integer label for land surface scheme

        Args:
            key (str, optional): Name of land surface scheme. Defaults to "noah".
        """
        # Here is the map of scheme name and integer label in WRF
        # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/physics.html#lsm-scheme-details-and-references
        integer_label_map = {
            "off": cls.OFF,
            "slab": cls.SLAB,
            "noah": cls.NOAH,
            "ruc": cls.RUC,
            "noah-mp": cls.NOAH_MP,
            "clm4": cls.CLM4,
            "px": cls.PLEIM_XIU,
            "ssib": cls.SSIB
        }

        # check if key is in map
        if key not in integer_label_map:
            logger.error(
                f"Key error: {key}. Valid key: {list(integer_label_map.keys())}"
            )
            raise KeyError

        return integer_label_map[key]


@dataclass()
class SchemeSurfaceLayer:
    """
    Surface layer physics schemes.
    """
    OFF = 0
    MM5 = 1
    MONIN_OBUKHOV = 2
    QNSE = 4
    MYNN = 5
    PLEIM_XIU = 7
    TEMF = 10
    OLD_MM5 = 91

    @classmethod
    def get_scheme_id(cls, key: str = "mm5"):
        """Get corresponding integer label for surface layer scheme

        Args:
            key (str, optional): Name of surface layer scheme. Defaults to "mo".
        """
        # Here is the map of scheme name and integer label in WRF
        # Reference link: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/namelist_variables.html
        integer_label_map = {
            "off": cls.OFF,
            "mm5": cls.MM5,
            "mo": cls.MONIN_OBUKHOV,
            "qnse": cls.QNSE,
            "mynn": cls.MYNN,
            "px": cls.PLEIM_XIU,
            "temf": cls.TEMF,
            "old-mm5": cls.OLD_MM5
        }

        # check if key is in map
        if key not in integer_label_map:
            logger.error(
                f"Key error: {key}. Valid key: {list(integer_label_map.keys())}"
            )
            raise KeyError

        return integer_label_map[key]


__all__ = ["SchemeCumulus", "SchemeLandSurfaceModel", "SchemeLongWave", "SchemePBL", "SchemeShortWave", "SchemeSurfaceLayer"]
