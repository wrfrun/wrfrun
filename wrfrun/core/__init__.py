"""
wrfrun.core
###########

The core functionalities of ``wrfrun`` are all implemented in the submodule ``wrfrun.core``,
such as processing namelist files, managing resource files required during model's running (e.g., VTable files),
calling the numerical model and process its output and log files, monitoring simulation process via model's log,
recording and replaying the simulation.

The functionalities are split into several submodules, which are listed in the table below.

Submodules
**********

================================ ========================================================
:doc:`base </api/core.base>`     Executable base class and related classes.
:doc:`config </api/core.config>` ``wrfrun`` config classes.
:doc:`error </api/core.error>`   ``wrfrun`` error classes.
:doc:`replay </api/core.replay>` Functions and classes to record and replay simulations.
:doc:`server </api/core.server>` Functions and classes to start socket server.
================================ ========================================================

.. toctree:: 
    :maxdepth: 1
    :hidden:

    base <core.base>
    config <core.config>
    error <core.error>
    replay <core.replay>
    server <core.server>
"""

from .base import *
from .config import *
from .error import *
from .replay import *
from .server import *
