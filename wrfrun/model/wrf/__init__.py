"""
wrfrun.model.wrf
################

WRF and WPS model integration.

Submodules
**********

====================================================================== ========================================================
:doc:`core </api/model.wrf.core>`                                         WPS and WRF executable implementations.
:doc:`exec_wrap </api/model.wrf.exec_wrap>`                               Function wrappers for WPS and WRF executables.
:doc:`geodata </api/model.wrf.geodata>`                                   WPS geographical-static-data readers.
:doc:`log </api/model.wrf.log>`                                           WPS and WRF log helpers.
:doc:`namelist </api/model.wrf.namelist>`                                 WPS and WRF namelist preparation.
:doc:`plot </api/model.wrf.plot>`                                         WRF domain plotting settings.
:doc:`plugin </api/model.wrf.plugin>`                                     WRF plugin registration.
:doc:`scheme </api/model.wrf.scheme>`                                     WRF physics-scheme identifiers.
:doc:`utils </api/model.wrf.utils>`                                       WRF utility functions.
:doc:`vtable </api/model.wrf.vtable>`                                     WPS Vtable resource references.
:doc:`workspace </api/model.wrf.workspace>`                               WRF workspace preparation and validation.
====================================================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    core <model.wrf.core>
    exec_wrap <model.wrf.exec_wrap>
    geodata <model.wrf.geodata>
    log <model.wrf.log>
    namelist <model.wrf.namelist>
    plot <model.wrf.plot>
    plugin <model.wrf.plugin>
    scheme <model.wrf.scheme>
    utils <model.wrf.utils>
    vtable <model.wrf.vtable>
    workspace <model.wrf.workspace>
"""

from .core import DFI, WRF, GeoGrid, LinkGrib, MetGrid, NDown, Real, UnGrib
from .exec_wrap import dfi, geogrid, metgrid, ndown, real, ungrib, wrf
from .geodata import parse_geographical_data_file, parse_geographical_data_index, read_geographical_static_data
from .namelist import (
    get_metgrid_fg_names,
    get_ungrib_out_dir_path,
    get_ungrib_out_prefix,
    prepare_dfi_namelist,
    prepare_wps_namelist,
    prepare_wrf_namelist,
    prepare_wrfda_namelist,
    set_metgrid_fg_names,
    set_ungrib_out_prefix,
)
from .scheme import (
    SchemeCumulus,
    SchemeLandSurfaceModel,
    SchemeLongWave,
    SchemeMicrophysics,
    SchemePBL,
    SchemeShortWave,
    SchemeSurfaceLayer,
)
from .vtable import VtableFiles

__all__ = [
    "DFI",
    "GeoGrid",
    "LinkGrib",
    "MetGrid",
    "NDown",
    "Real",
    "SchemeCumulus",
    "SchemeLandSurfaceModel",
    "SchemeLongWave",
    "SchemeMicrophysics",
    "SchemePBL",
    "SchemeShortWave",
    "SchemeSurfaceLayer",
    "UnGrib",
    "VtableFiles",
    "WRF",
    "dfi",
    "geogrid",
    "get_metgrid_fg_names",
    "get_ungrib_out_dir_path",
    "get_ungrib_out_prefix",
    "metgrid",
    "ndown",
    "parse_geographical_data_file",
    "parse_geographical_data_index",
    "prepare_dfi_namelist",
    "prepare_wps_namelist",
    "prepare_wrf_namelist",
    "prepare_wrfda_namelist",
    "read_geographical_static_data",
    "real",
    "set_metgrid_fg_names",
    "set_ungrib_out_prefix",
    "ungrib",
    "wrf",
]
