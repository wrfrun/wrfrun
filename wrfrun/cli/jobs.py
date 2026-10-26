"""CLI handlers for run-status commands."""

import argparse

from rich.table import Table

from ..core.operations.jobs import follow_job_log, get_job, list_jobs
from ..log import get_wrfrun_rich_console


def entry_jobs(args: argparse.Namespace):
    """List active runs or follow one external command's output."""
    if args.follow is not None:
        job = get_job(args.config, args.follow)
        for output in follow_job_log(job, args.stream):
            get_wrfrun_rich_console().print(output, end="", markup=False)
        return

    table = Table(title="Active wrfrun jobs")
    table.add_column("Experiment")
    table.add_column("Run ID", style="cyan")
    table.add_column("State")
    table.add_column("Executable")
    table.add_column("Started")
    table.add_column("Updated")
    for job in list_jobs(args.config):
        table.add_row(
            job.status["experiment"],
            job.run_id,
            job.status["state"],
            job.status["current_executable"] or "-",
            job.status["started_at"],
            job.status["updated_at"],
        )
    get_wrfrun_rich_console().print(table)
