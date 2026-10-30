"""
wrfrun.scheduler.backend
########################

Shared scheduler backend interface.

.. autosummary::
    :toctree: generated/

    SchedulerBackend
    get_scheduler_backend
"""

from pathlib import Path
from typing import Protocol

from .lsf import LSFBackend
from .pbs import PBSBackend
from .slurm import SlurmBackend


class SchedulerBackend(Protocol):
    """Submit scheduler jobs and identify the current scheduler job."""

    name: str

    def submit(self, script_path: Path) -> str | None:
        """Submit a script and return its scheduler job ID when available."""
        ...

    def detect_job_id(self) -> str | None:
        """Return the current scheduler job ID from the environment."""
        ...


_BACKENDS: dict[str, SchedulerBackend] = {
    "lsf": LSFBackend(),
    "pbs": PBSBackend(),
    "slurm": SlurmBackend(),
}


def get_scheduler_backend(name: str) -> SchedulerBackend:
    """Return the backend registered under ``name``."""
    try:
        return _BACKENDS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scheduler name: {name}") from exc


__all__ = ["SchedulerBackend", "get_scheduler_backend"]
