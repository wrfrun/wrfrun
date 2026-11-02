"""
wrfrun.model.arps
#################

ARPS model integration.

Submodules
**********

====================================================================== ========================================================
:doc:`core </api/model.arps.core>`                                         ARPS executable implementations.
:doc:`exec_wrap </api/model.arps.exec_wrap>`                               Function wrappers for ARPS executables.
:doc:`io </api/model.arps.io>`                                             Conditional ARPS input and output rules.
:doc:`plugin </api/model.arps.plugin>`                                     ARPS plugin registration.
:doc:`workspace </api/model.arps.workspace>`                               ARPS workspace preparation and validation.
====================================================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    core <model.arps.core>
    exec_wrap <model.arps.exec_wrap>
    io <model.arps.io>
    plugin <model.arps.plugin>
    workspace <model.arps.workspace>
"""

from .core import ARPS, ARPSSFC, EXT2ARPS, ARPS3DVar, ARPSIntrp, ARPSTrn, RadRemap
from .exec_wrap import arps, arps3dvar, arpsintrp, arpssfc, arpstrn, ext2arps, radremap
from .plugin import ARPSPlugin
from .workspace import check_arps_workspace, prepare_arps_workspace

__all__ = [
    "ARPS",
    "ARPS3DVar",
    "ARPSIntrp",
    "ARPSSFC",
    "ARPSTrn",
    "ARPSPlugin",
    "EXT2ARPS",
    "RadRemap",
    "arps",
    "arps3dvar",
    "arpsintrp",
    "arpssfc",
    "arpstrn",
    "check_arps_workspace",
    "ext2arps",
    "prepare_arps_workspace",
    "radremap",
]
