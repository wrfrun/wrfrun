"""
wrfrun.model
############

To be able to handle different numerical models,
``wrfrun`` implements various ``Executable`` for model's binary executable
based on :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`,
which are all placed in this module.

``wrfrun.model`` currently supports following numerical models:

========================================= ==========================================
:doc:`arps </api/model.arps>`             Support for ARPS
:doc:`constants </api/model.constants>`   Definition of contants used by models.
:doc:`palm </api/model.palm>`             Support for PALM
:doc:`plot </api/model.plot>`             Plot submodule.
:doc:`plugins </api/model.plugins>`       Model plugin load functions.
:doc:`roms </api/model.roms>`             Support for ROMS
:doc:`type </api/model.type>`             Definition of types used by models.
:doc:`utils </api/model.utils>`           Utility functions.
:doc:`wrf </api/model.wrf>`               Support for WRF
========================================= ==========================================

.. toctree::
    :maxdepth: 1
    :hidden:

    arps <model.arps>
    constants <model.constants>
    palm <model.palm>
    plot <model.plot>
    plugins <model.plugins>
    roms <model.roms>
    type <model.type>
    utils <model.utils>
    wrf <model.wrf>
"""

from .constants import *
from .plot import *
from .plugins import *
from .type import *
from .utils import *
