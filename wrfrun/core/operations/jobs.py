"""
wrfrun.core.operations.jobs
############################

Read run status files and follow external-command logs.

.. autosummary::
    :toctree: generated/

    Job
    list_jobs
    get_job
    follow_job_log
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import tomli

ACTIVE_STATES = {"preparing", "submitted", "running"}
TERMINAL_STATES = {"succeeded", "failed", "cancelled"}


@dataclass(frozen=True)
class Job:
    """Describe one run recorded by a status file."""

    status_path: Path
    status: dict

    @property
    def run_id(self) -> str:
        """Return the run identifier."""
        return self.status["run_id"]

    def refresh(self) -> "Job":
        """Return this job with its latest saved status."""
        return Job(self.status_path, json.loads(self.status_path.read_text()))


def _run_root(config_path: str | Path) -> Path:
    config_file = Path(config_path).resolve()
    with config_file.open("rb") as config_handle:
        work_dir = Path(tomli.load(config_handle).get("work_dir", ".wrfrun"))

    if not work_dir.is_absolute():
        work_dir = config_file.parent / work_dir

    return work_dir / "runs"


def list_jobs(config_path: str | Path, active_only: bool = True) -> list[Job]:
    """List runs recorded for a project configuration file."""
    run_root = _run_root(config_path)
    if not run_root.is_dir():
        return []

    jobs = [Job(path, json.loads(path.read_text())) for path in run_root.glob("*/*/status.json")]
    if active_only:
        jobs = [job for job in jobs if job.status["state"] in ACTIVE_STATES]

    return sorted(jobs, key=lambda job: job.status["updated_at"], reverse=True)


def get_job(config_path: str | Path, run_id: str) -> Job:
    """Return one run identified by its run ID."""
    for job in list_jobs(config_path, active_only=False):
        if job.run_id == run_id:
            return job

    raise KeyError(f"Run '{run_id}' was not found.")


def follow_job_log(job: Job, stream: str = "stdout", interval: float = 0.5) -> Iterator[str]:
    """Yield new output from the current command until the run reaches a terminal state."""
    position = 0
    current_path = None

    while True:
        job = job.refresh()
        stream_path = job.status.get(stream)
        if stream_path is not None:
            log_path = Path(stream_path)
            if log_path != current_path:
                current_path = log_path
                position = 0

            if log_path.is_file():
                with log_path.open() as log_handle:
                    log_handle.seek(position)
                    output = log_handle.read()
                    position = log_handle.tell()

                if output:
                    yield output
                    continue

        if job.status["state"] in TERMINAL_STATES:
            return

        time.sleep(interval)


__all__ = ["Job", "follow_job_log", "get_job", "list_jobs"]
