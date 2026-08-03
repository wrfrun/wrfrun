"""
wrfrun.model.palm
#################

Implementation of PALM model.

Submodules
**********

============================================ ==================================================================================
:doc:`config </api/model.palm.config>`       Functions to process PALM config files.
:doc:`core </api/model.palm.core>`           Core implementation of PALM model.
:doc:`namelist </api/model.palm.namelist>`   Functions to process PALM namelist files.
:doc:`utils </api/model.palm.utils>`         Utilitiy functions.
============================================ ==================================================================================

About the implementation of PALM
********************************

Since ``PALM`` provides a bash script ``palmrun`` to take care of the running of ``palm``,
``wrfrun`` just simply wraps the bash script.

.. toctree::
    :maxdepth: 1
    :hidden:

    config <model.palm.config>
    core <model.palm.core>
    namelist <model.palm.namelist>
    utils <model.palm.utils>
"""

from .config import *
from .core import *
from .namelist import *
from .utils import *
