"""
wrfrun.model
############

To be able to handle different numerical models,
``wrfrun`` implements various ``Executable`` for model's binary executable
based on :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`,
which are all placed in this module.

``wrfrun.model`` currently supports following numerical models:

========================================= ==========================================
:doc:`palm </api/model.palm>`             Support for PALM
:doc:`wrf </api/model.wrf>`               Support for WRF
========================================= ==========================================

.. toctree::
    :maxdepth: 1
    :hidden:

    constants <model.constants>
    palm <model.palm>
    plot <model.plot>
    type <model.type>
    utils <model.utils>
    wrf <model.wrf>
"""

# just to register executables
from . import palm as _
from . import wrf as _
from .constants import *
from .plot import *
from .utils import *
