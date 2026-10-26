"""
wrfrun.core.runtime.status
##########################

Persist the lifecycle and current command of one simulation run.

.. autosummary::
    :toctree: generated/

    RunStatusService
"""

import json
import os
import socket
from datetime import datetime
from pathlib import Path

from .resource import ResourceCatalog


class RunStatusService:
    """Write the status file consumed by job-management clients."""

    def __init__(self, resource: ResourceCatalog):
        """Create a status service for one session's resource catalog."""
        self._resource = resource
        self._status: dict = {}

    @property
    def path(self) -> Path:
        """Return the current run's status file path."""
        return self._resource.layout.workspace_dir.parent / "status.json"

    @property
    def state(self) -> str | None:
        """Return the current run state."""
        return self._status.get("state")

    def start(self):
        """Create a status file for a newly entered run context."""
        layout = self._resource.layout
        now = self._timestamp()
        self._status = {
            "version": 1,
            "experiment": layout.experiment,
            "run_id": layout.run_id,
            "state": "preparing",
            "started_at": now,
            "updated_at": now,
            "finished_at": None,
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "current_executable": None,
            "command": None,
            "stdout": None,
            "stderr": None,
            "returncode": None,
            "timed_out": False,
            "error": None,
        }
        self._write()

    def update(self, state: str | None = None, **values):
        """Update the current status and persist it atomically."""
        if state is not None:
            values["state"] = state

        self._status.update(values)
        self._status["updated_at"] = self._timestamp()
        self._write()

    def start_command(self, executable: str, command: tuple[str, ...], stdout: Path, stderr: Path):
        """Record the external command currently being executed."""
        self.update(
            "running",
            current_executable=executable,
            command=list(command),
            stdout=str(stdout),
            stderr=str(stderr),
            returncode=None,
            timed_out=False,
            error=None,
        )

    def finish_command(self, returncode: int):
        """Record a successfully completed external command."""
        self.update(returncode=returncode)

    def fail(self, error: str, returncode: int | None = None, timed_out: bool = False):
        """Record a failed command or run context."""
        self.update(
            "failed",
            error=error,
            returncode=returncode,
            timed_out=timed_out,
            finished_at=self._timestamp(),
        )

    def finish(self):
        """Record that the run context completed successfully."""
        self.update("succeeded", finished_at=self._timestamp())

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def _write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(self._status, indent=2) + "\n")
        temporary_path.replace(self.path)


__all__ = ["RunStatusService"]
