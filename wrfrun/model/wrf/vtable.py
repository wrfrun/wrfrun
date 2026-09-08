"""
wrfrun.model.wrf.vtable
#######################

Dataclasses to represents VTable files in WRF.

.. autosummary::
    :toctree: generated/

    VtableFiles

How to use
**********

Attributes of :class:`VtableFiles` is a ``wrfrun`` URI, parse it will get the real path of VTable files.

**For example**

.. code-block:: python
    :caption: main.py

    from wrfrun.core import WRFRUN
    from wrfrun.model.wrf import VtableFiles

    vtable_real_file_path = WRFRUN.config.parse_resource_uri(VtableFiles.ERA_PL)
"""

from dataclasses import dataclass

from wrfrun.core import ResourceRef

VTABLE_URI = ResourceRef("model_wps", "ungrib/Variable_Tables")


@dataclass
class VtableFiles:
    """
    Represent WPS Vtable files (v4.5).

    **NOTE**

    This class doesn't have method to check if the VTable file exists.
    User need to check the VTable file when use it.
    """

    AFWAICE = VTABLE_URI / "Vtable.AFWAICE"
    AGRMETSNOW = VTABLE_URI / "Vtable.AGRMETSNOW"
    AGRMETSOIL = VTABLE_URI / "Vtable.AGRMETSOIL"
    AGRMETSOIL2 = VTABLE_URI / "Vtable.AGRMETSOIL2"
    AGRWRF = VTABLE_URI / "Vtable.AGRWRF"
    ARW = VTABLE_URI / "Vtable.ARW.UPP"
    ARWP = VTABLE_URI / "Vtable.ARWp.UPP"
    AVN0P5WRF = VTABLE_URI / "Vtable.AVN0P5WRF"
    AWIP = VTABLE_URI / "Vtable.AWIP"
    CFSR = VTABLE_URI / "Vtable.CFSR"
    CFSR_MEAN = VTABLE_URI / "Vtable.CFSR_mean"
    ECMWF = VTABLE_URI / "Vtable.ECMWF"
    ECMWF_SIGMA = VTABLE_URI / "Vtable.ECMWF_sigma"
    ERA_ML = VTABLE_URI / "Vtable.ERA-interim.ml"
    ERA_PL = VTABLE_URI / "Vtable.ERA-interim.pl"
    GFDL = VTABLE_URI / "Vtable.GFDL"
    GFS = VTABLE_URI / "Vtable.GFS"
    GFS_OZONE = VTABLE_URI / "Vtable.GFS_OZONE"
    GFSENS = VTABLE_URI / "Vtable.GFSENS"
    GODAS = VTABLE_URI / "Vtable.GODAS"
    GSM = VTABLE_URI / "Vtable.GSM"
    ICONM = VTABLE_URI / "Vtable.ICONm"
    ICONP = VTABLE_URI / "Vtable.ICONp"
    JMAGSM = VTABLE_URI / "Vtable.JMAGSM"
    NAM = VTABLE_URI / "Vtable.NAM"
    NARR = VTABLE_URI / "Vtable.NARR"
    NAVY_SST = VTABLE_URI / "Vtable.NavySST"
    NCEP2 = VTABLE_URI / "Vtable.NCEP2"
    NNRP = VTABLE_URI / "Vtable.NNRP"
    NOGAPS = VTABLE_URI / "Vtable.NOGAPS"
    NOGAPS_GFS_SOIL = VTABLE_URI / "Vtable.NOGAPS_needs_GFS_soil"
    RAP_HYBRID_NCEP = VTABLE_URI / "Vtable.RAP.hybrid.ncep"
    RAP_PRESSURE_NCEP = VTABLE_URI / "Vtable.RAP.pressure.ncep"
    RAP_SIGMA_GSD = VTABLE_URI / "Vtable.RAP.sigma.gsd"
    RAPHRRR = VTABLE_URI / "Vtable.raphrrr"
    RUCB = VTABLE_URI / "Vtable.RUCb"
    RUCP = VTABLE_URI / "Vtable.RUCp"
    SREF = VTABLE_URI / "Vtable.SREF"
    SST = VTABLE_URI / "Vtable.SST"
    TCRP = VTABLE_URI / "Vtable.TCRP"
    UKMO_END_GAME = VTABLE_URI / "Vtable.UKMO_ENDGame"
    UKMO_LANDSEA = VTABLE_URI / "Vtable.UKMO_LANDSEA"
    UKMO_NO_HEIGHTS = VTABLE_URI / "Vtable.UKMO_no_heights"


__all__ = ["VtableFiles"]
