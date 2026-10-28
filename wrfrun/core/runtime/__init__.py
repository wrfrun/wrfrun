"""
wrfrun.core.runtime
###################

wrfrun runtime services which will be shared across all sessions.

Submodules
**********

============================================== ========================================================
:doc:`io </api/core.runtime.io>`               ``wrfrun`` IO service.
:doc:`port </api/core.runtime.port>`           Runtime service port.
:doc:`record </api/core.runtime.record>`       Record service.
:doc:`registry </api/core.runtime.registry>`   ``wrfrun`` ``Executable`` registry.
:doc:`resource </api/core.runtime.resource>`   ``wrfrun`` resource service.
:doc:`runner </api/core.runtime.runner>`       ``wrfrun`` external command runner service.
:doc:`status </api/core.runtime.status>`       Persistent simulation run status service.
:doc:`workspace </api/core.runtime.workspace>` ``wrfrun`` workspace service.
============================================== ========================================================

``wrfrun`` Project
******************

A typical ``wrfrun`` project has following directories:

* ``data``: Directory which stores input and output data.
  * ``inputs``: Directory which stores input data.
    * ``common``: Directory which stores shared model inputs.
    * ``experiments``: Directory which stores experiment-specific inputs.
  * ``outputs``: Directory which stores output data.
    * ``<run-id>``: Immutable outputs archived from one run.
    * ``results``: Latest archived results of each executable in one experiment.
* ``configs``: Directory which stores ``wrfrun`` configs.
  * ``experiments``: Directory which stores experiment configuration overrides.
  * ``namelists``: Direcctory which stores namelists used by external models.
    * ``templates``: Directory which stores namelists template.
    * ``user``: Directory which stores user's namelists.
* ``logs``: Directory which stores model logs.
* ``.wrfrun/runs``: Directory which stores isolated workspaces, replay files,
  and temporary files for each experiment run.

.. toctree::
    :maxdepth: 1
    :hidden:

    io <core.runtime.io>
    port <core.runtime.port>
    record <core.runtime.record>
    registry <core.runtime.registry>
    resource <core.runtime.resource>
    runner <core.runtime.runner>
    status <core.runtime.status>
    workspace <core.runtime.workspace>
"""

from .io import *
from .port import *
from .record import *
from .registry import *
from .resource import *
from .runner import *
from .status import *
from .workspace import *
