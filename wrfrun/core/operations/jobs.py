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
READ_CHUNK_SIZE = 64 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_BACKLOG_BYTES = 16 * 1024 * 1024
INITIAL_TAIL_LINES = 100


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


def _read_log_tail(log_path: Path) -> tuple[bytes, bytes, int]:
    """Read the latest complete log lines without loading the whole file."""
    size = log_path.stat().st_size
    start = max(0, size - MAX_OUTPUT_BYTES)

    with log_path.open("rb") as log_handle:
        log_handle.seek(start)
        data = log_handle.read(MAX_OUTPUT_BYTES)

    if start:
        _, separator, data = data.partition(b"\n")
        if not separator:
            return b"", data, size

    complete, separator, partial = data.rpartition(b"\n")
    if not separator:
        return b"", partial, size

    lines = (complete + separator).splitlines(keepends=True)
    return b"".join(lines[-INITIAL_TAIL_LINES:]), partial, size


def follow_job_log(job: Job, stream: str = "stdout", interval: float = 0.5) -> Iterator[str]:
    """Yield bounded, line-oriented output from the current command log."""
    position = 0
    current_path = None
    partial_line = b""

    while True:
        job = job.refresh()
        stream_path = job.status.get(stream)
        if stream_path is not None:
            log_path = Path(stream_path)
            if log_path.is_file():
                if log_path != current_path:
                    current_path = log_path
                    output, partial_line, position = _read_log_tail(log_path)
                    if output:
                        yield output.decode(errors="replace")

                size = log_path.stat().st_size
                if size < position:
                    position = 0
                    partial_line = b""

                backlog = size - position
                if backlog > MAX_BACKLOG_BYTES:
                    position = size
                    partial_line = b""
                    yield f"[wrfrun] Skipped {backlog / 1024**2:.1f} MiB of log output to keep up.\n"
                elif backlog:
                    remaining = min(backlog, MAX_OUTPUT_BYTES)
                    with log_path.open("rb") as log_handle:
                        log_handle.seek(position)
                        while remaining:
                            chunk = log_handle.read(min(READ_CHUNK_SIZE, remaining))
                            if not chunk:
                                break

                            position += len(chunk)
                            remaining -= len(chunk)
                            complete, separator, partial_line = (partial_line + chunk).rpartition(b"\n")
                            if separator:
                                yield (complete + separator).decode(errors="replace")

        if job.status["state"] in TERMINAL_STATES:
            if partial_line:
                yield partial_line.decode(errors="replace")
            return

        time.sleep(interval)


__all__ = ["Job", "follow_job_log", "get_job", "list_jobs"]
