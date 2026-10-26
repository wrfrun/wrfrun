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

====================================== ========================================================
:doc:`base </api/core.base>`           Definition of ``Executable`` base class.
:doc:`core </api/core.core>`           Definition of proxy class ``WRFRUNProxy``.
:doc:`error </api/core.error>`         Definition of ``wrfrun`` error exceptions.
:doc:`operations </api/operations>`    Project and run management operations.
:doc:`plugin </api/core.plugin>`       Definition of plugin protocol.
:doc:`runtime </api/core.runtime>`     Definition of runtime service.
:doc:`server </api/core.server>`       Functions and classes to start socket server.
:doc:`states </api/core.states>`       Definition of session states.
:doc:`type </api/core.type>`           Definition of various types used in ``wrfrun``.
====================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    base <core.base>
    core <core.core>
    error <core.error>
    operations <operations>
    plugin <core.plugin>
    server <core.server>
    type <core.type>
"""

from .base import *
from .core import *
from .error import *
from .plugin import *
from .runtime import *
from .server import *
from .states import *
from .type import *
