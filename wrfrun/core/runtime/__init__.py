"""
wrfrun.core.runtime
###################

wrfrun runtime services which will be shared across all sessions.

Submodules
**********

============================================== ========================================================
:doc:`io </api/core.runtime.io>`               ``wrfrun`` IO service.
:doc:`resource </api/core.runtime.resource>`   ``wrfrun`` resource service.
============================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    io <core.runtime.io>
    resource <core.runtime.resource>
"""

from .io import *
from .resource import *
