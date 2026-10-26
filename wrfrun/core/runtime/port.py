"""
wrfrun.core.runtime.port
########################

Runtime service port.

.. autosummary::
    :toctree: generated/


"""

from dataclasses import dataclass

from .io import IOService
from .record import ReplayService
from .registry import ExecutableRegistry
from .resource import ResourceCatalog
from .runner import RunnerService
from .status import RunStatusService
from .workspace import WorkspaceService


@dataclass(frozen=True)
class RuntimeService:
    """
    Runtime service port.
    """

    io: IOService
    """
    IO service.
    """

    replay: ReplayService
    """
    Record and replay service.
    """

    registry: ExecutableRegistry
    """
    ``Executable`` registry service.
    """

    resource: ResourceCatalog
    """
    Resource manager service.
    """

    runner: RunnerService
    """
    External command runner service.
    """

    workspace: WorkspaceService
    """
    Workspace service.
    """

    status: RunStatusService
    """
    Persistent run status service.
    """


__all__ = ["RuntimeService"]
