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
:doc:`_config </api/core._config>`     Definition of ``WRFRunConfig``.
:doc:`_constant </api/core._constant>` Definition of ``ConstantMixIn``.
:doc:`_exec_db </api/core._exec_db>`   Definition of ``ExecutableDB``.
:doc:`_namelist </api/core._namelist>` Definition of ``NamelistMixIn``.
:doc:`_record </api/core._record>`     Definition of ``ExecutableRecorder``.
:doc:`_resource </api/core._resource>` Definition of ``ResourceMixIn``.
:doc:`base </api/core.base>`           Definition of ``Executable`` base class.
:doc:`core </api/core.core>`           Definition of proxy class ``WRFRUNProxy``.
:doc:`error </api/core.error>`         Definition of ``wrfrun`` error exceptions.
:doc:`replay </api/core.replay>`       Functions and classes to replay simulations.
:doc:`server </api/core.server>`       Functions and classes to start socket server.
:doc:`type </api/core.type>`           Definition of various types used in ``wrfrun``.
====================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    _config <core._config>
    _constant <core._constant>
    _exec_db <core._exec_db>
    _namelist <core._namelist>
    _record <core._record>
    _resource <core._resource>
    base <core.base>
    core <core.core>
    error <core.error>
    replay <core.replay>
    server <core.server>
    type <core.type>
"""

from ._config import *
from ._exec_db import *
from .base import *
from .core import *
from .error import *
from .replay import *
from .server import *
from .type import *
