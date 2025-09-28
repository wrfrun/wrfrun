"""
wrfrun.model
############

To be able to handle different numerical models,
``wrfrun`` implements various ``Executable`` for model's binary executable based on :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`,
which are all placed in this module.

``wrfrun.model`` currently supports following numerical models:

========================================= ==========================================
:doc:`wrf </api/model.wrf>`               Support for WRF
========================================= ==========================================

.. toctree::
    :maxdepth: 1
    :hidden:

    wrf <model.wrf>
    base <model.base>
    plot <model.plot>
    utils <model.utils>
"""

from .base import *
from .plot import *
from .utils import *

# just to register executables
from . import wrf
