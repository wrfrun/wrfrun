"""
wrfrun.core.runtime
###################

Runtime services shared by one ``wrfrun`` session.

Submodules
**********

================================================= ========================================================
:doc:`io </api/core.runtime.io>`                  File copying, linking, and writing.
:doc:`port </api/core.runtime.port>`              Runtime service container.
:doc:`record </api/core.runtime.record>`          Replay archive creation and loading.
:doc:`registry </api/core.runtime.registry>`      Executable registration.
:doc:`resource </api/core.runtime.resource>`      Project resources and run paths.
:doc:`runner </api/core.runtime.runner>`          External command execution.
:doc:`status </api/core.runtime.status>`          Persistent run-status records.
:doc:`workspace </api/core.runtime.workspace>`    Workspace initialization and cleanup.
================================================= ========================================================

Project layout
**************

A typical ``wrfrun`` project contains the following directories::

    data/
        inputs/
            common/       # Shared model inputs.
            experiments/  # Experiment-specific inputs.
        outputs/
            <run-id>/     # Immutable outputs from one run.
            results/      # Latest result of each executable.
    configs/
        experiments/      # Experiment configuration overrides.
        namelists/
            templates/    # Namelist templates.
            user/         # User namelist overrides.
    logs/
    .wrfrun/runs/         # Workspaces, replay files, and temporary files.

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

from .io import IOService
from .port import RuntimeService
from .record import ReplayService
from .registry import ExecutableRegistry
from .resource import PROJECT_TREE, ResourceCatalog, RunLayout
from .runner import Command, CommandResult, CommandStdStream, RunnerService, StreamMode
from .status import RunStatusService
from .workspace import WorkspaceService

__all__ = [
    "Command",
    "CommandResult",
    "CommandStdStream",
    "ExecutableRegistry",
    "IOService",
    "PROJECT_TREE",
    "ReplayService",
    "ResourceCatalog",
    "RunLayout",
    "RunnerService",
    "RunStatusService",
    "RuntimeService",
    "StreamMode",
    "WorkspaceService",
]
