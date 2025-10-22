"""
wrfrun.model.wrf
################

Implementation of WRF model.

Submodules
**********

============================================ ==================================================================================
:doc:`_metgrid </api/model.wrf._metgrid>`    Utility functions used by :class:`MetGrid <core.MetGrid>`.
:doc:`_ndown </api/model.wrf._ndown>`        Utility functions used by :class:`NDown <core.NDown>`.
:doc:`core </api/model.wrf.core>`            Core implementation of WRF model.
:doc:`exec_wrap </api/model.wrf.exec_wrap>`  Function wrappers for ``Executable`` defined in :doc:`core </api/model.wrf.core>`.
:doc:`geodata </api/model.wrf.geodata>`      Utility functions to read / write geographical static datas.
:doc:`namelist </api/model.wrf.namelist>`    Functions to process WPS / WRF namelist files.
:doc:`plot </api/model.wrf.plot>`            Functions to create projection from namelist settings to plot simulation domain.
:doc:`scheme </api/model.wrf.scheme>`        Scheme ``dataclass``.
:doc:`vtable </api/model.wrf.vtable>`        Vtable files ``dataclass``.
============================================ ==================================================================================

.. autosummary::
    :toctree: generated/

    prepare_namelist

.. toctree::
    :maxdepth: 1
    :hidden:

    _metgrid <model.wrf._metgrid>
    _ndown <model.wrf._ndown>
    core <model.wrf.core>
    exec_wrap <model.wrf.exec_wrap>
    geodata <model.wrf.geodata>
    namelist <model.wrf.namelist>
    plot <model.wrf.plot>
    scheme <model.wrf.scheme>
    vtable <model.wrf.vtable>
"""

from .core import *
from .exec_wrap import *
from .geodata import *
from .namelist import *
from .scheme import *
from .vtable import *
