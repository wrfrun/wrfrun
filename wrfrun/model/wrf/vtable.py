from dataclasses import dataclass

from wrfrun.core import WRFRUNConfig
from wrfrun.workspace.wrf import WORKSPACE_MODEL_WPS


VTABLE_URI = ":WRFRUN_VTABLE:"


@dataclass
class VtableFiles:
    """
    Represent WPS Vtable files (v4.5).
    With the ":/" we can tell from user custom Vtable files.
    """
    AFWAICE = f"{VTABLE_URI}/Vtable.AFWAICE"
    AGRMETSNOW = f"{VTABLE_URI}/Vtable.AGRMETSNOW"
    AGRMETSOIL = f"{VTABLE_URI}/Vtable.AGRMETSOIL"
    AGRMETSOIL2 = f"{VTABLE_URI}/Vtable.AGRMETSOIL2"
    AGRWRF = f"{VTABLE_URI}/Vtable.AGRWRF"
    ARW = f"{VTABLE_URI}/Vtable.ARW.UPP"
    ARWP = f"{VTABLE_URI}/Vtable.ARWp.UPP"
    AVN0P5WRF = f"{VTABLE_URI}/Vtable.AVN0P5WRF"
    AWIP = f"{VTABLE_URI}/Vtable.AWIP"
    CFSR = f"{VTABLE_URI}/Vtable.CFSR"
    CFSR_MEAN = f"{VTABLE_URI}/Vtable.CFSR_mean"
    ECMWF = f"{VTABLE_URI}/Vtable.ECMWF"
    ECMWF_SIGMA = f"{VTABLE_URI}/Vtable.ECMWF_sigma"
    ERA_ML = f"{VTABLE_URI}/Vtable.ERA-interim.ml"
    ERA_PL = f"{VTABLE_URI}/Vtable.ERA-interim.pl"
    GFDL = f"{VTABLE_URI}/Vtable.GFDL"
    GFS = f"{VTABLE_URI}/Vtable.GFS"
    GFS_OZONE = f"{VTABLE_URI}/Vtable.GFS_OZONE"
    GFSENS = f"{VTABLE_URI}/Vtable.GFSENS"
    GODAS = f"{VTABLE_URI}/Vtable.GODAS"
    GSM = f"{VTABLE_URI}/Vtable.GSM"
    ICONM = f"{VTABLE_URI}/Vtable.ICONm"
    ICONP = f"{VTABLE_URI}/Vtable.ICONp"
    JMAGSM = f"{VTABLE_URI}/Vtable.JMAGSM"
    NAM = f"{VTABLE_URI}/Vtable.NAM"
    NARR = f"{VTABLE_URI}/Vtable.NARR"
    NAVY_SST = f"{VTABLE_URI}/Vtable.NavySST"
    NCEP2 = f"{VTABLE_URI}/Vtable.NCEP2"
    NNRP = f"{VTABLE_URI}/Vtable.NNRP"
    NOGAPS = f"{VTABLE_URI}/Vtable.NOGAPS"
    NOGAPS_GFS_SOIL = f"{VTABLE_URI}/Vtable.NOGAPS_needs_GFS_soil"
    RAP_HYBRID_NCEP = f"{VTABLE_URI}/Vtable.RAP.hybrid.ncep"
    RAP_PRESSURE_NCEP = f"{VTABLE_URI}/Vtable.RAP.pressure.ncep"
    RAP_SIGMA_GSD = f"{VTABLE_URI}/Vtable.RAP.sigma.gsd"
    RAPHRRR = f"{VTABLE_URI}/Vtable.raphrrr"
    RUCB = f"{VTABLE_URI}/Vtable.RUCb"
    RUCP = f"{VTABLE_URI}/Vtable.RUCp"
    SREF = f"{VTABLE_URI}/Vtable.SREF"
    SST = f"{VTABLE_URI}/Vtable.SST"
    TCRP = f"{VTABLE_URI}/Vtable.TCRP"
    UKMO_END_GAME = f"{VTABLE_URI}/Vtable.UKMO_ENDGame"
    UKMO_LANDSEA = f"{VTABLE_URI}/Vtable.UKMO_LANDSEA"
    UKMO_NO_HEIGHTS = f"{VTABLE_URI}/Vtable.UKMO_no_heights"


# register uri
if not WRFRUNConfig.check_resource_uri(VTABLE_URI):
    WRFRUNConfig.register_resource_uri(VTABLE_URI, f"{WORKSPACE_MODEL_WPS}/ungrib/Variable_Tables")


__all__ = ["VtableFiles"]
