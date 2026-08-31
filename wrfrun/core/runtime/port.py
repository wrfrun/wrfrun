"""
wrfrun.core.runtime.port
########################

Runtime service port.

.. autosummary::
    :toctree: generated/


"""

from dataclasses import dataclass

from .io import IOService
from .record import RecordService
from .registry import ExecutableRegistry
from .resource import ResourceCatalog


@dataclass(frozen=True)
class RuntimeService:
    """
    Runtime service port.
    """

    io: IOService
    """
    IO service.
    """

    record: RecordService
    """
    Record service.
    """

    registry: ExecutableRegistry
    """
    ``Executable`` registry service.
    """

    resource: ResourceCatalog
    """
    Resource manager service.
    """


__all__ = ["RuntimeService"]
