"""
wrfrun.model.wrf
################

Implementation of WRF model.

Submodules
**********

============================================ ==================================================================================
:doc:`core </api/model.wrf.core>`            Core implementation of WRF model.
:doc:`exec_wrap </api/model.wrf.exec_wrap>`  Function wrappers for ``Executable`` defined in :doc:`core </api/model.wrf.core>`.
:doc:`geodata </api/model.wrf.geodata>`      Utility functions to read / write geographical static datas.
:doc:`log </api/model.wrf.log>`              Functions to parse and clear WPS/WRF model logs.
:doc:`namelist </api/model.wrf.namelist>`    Functions to process WPS / WRF namelist files.
:doc:`plot </api/model.wrf.plot>`            Functions to create projection from namelist settings to plot simulation domain.
:doc:`scheme </api/model.wrf.scheme>`        Scheme ``dataclass``.
:doc:`utils </api/model.wrf.utils>`          Utility functions used by wrf model part.
:doc:`vtable </api/model.wrf.vtable>`        Vtable files ``dataclass``.
============================================ ==================================================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    core <model.wrf.core>
    exec_wrap <model.wrf.exec_wrap>
    geodata <model.wrf.geodata>
    log <model.wrf.log>
    namelist <model.wrf.namelist>
    plot <model.wrf.plot>
    scheme <model.wrf.scheme>
    utils <model.wrf.utils>
    vtable <model.wrf.vtable>
"""

from .core import *
from .exec_wrap import *
from .geodata import *
from .namelist import *
from .scheme import *
from .vtable import *
