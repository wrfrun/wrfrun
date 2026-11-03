"""
wrfrun.model.roms
#################

Experimental ROMS model integration.

Submodules
**********

====================================================================== ========================================================
:doc:`core </api/model.roms.core>`                                         ROMS executable and function wrapper.
:doc:`plugin </api/model.roms.plugin>`                                     ROMS plugin registration.
====================================================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    core <model.roms.core>
    plugin <model.roms.plugin>
"""

from .core import ROMS, roms

__all__ = ["ROMS", "roms"]
