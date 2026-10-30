"""
wrfrun.scheduler.slurm
######################

Scheduler interface for Slurm system.

.. autosummary::
    :toctree: generated/

    SlurmBackend
    slurm_generate_settings
"""

import logging
import re
from os import getenv
from pathlib import Path

from wrfrun.core import WRFRUN_NEW, call_subprocess
from wrfrun.res import SCHEDULER_SLURM_TEMPLATE

from .utils import get_core_num

LOGGER = logging.getLogger("wrfrun")


class SlurmBackend:
    """Submit and identify Slurm jobs."""

    name = "slurm"

    def submit(self, script_path: Path) -> str | None:
        """Submit ``script_path`` through ``sbatch`` and return its job ID."""
        result = call_subprocess(["sbatch", "--parsable", str(script_path)])
        job_id = result.stdout.decode(errors="replace").strip().split(";", maxsplit=1)[0]
        if re.fullmatch(r"\d+(?:_[\d,-]+)?", job_id) is None:
            LOGGER.warning("Could not read Slurm job ID from sbatch output. Check whether the task was submitted.")
            LOGGER.warning("sbatch stdout:\n%s", result.stdout.decode(errors="replace"))
            if result.stderr:
                LOGGER.warning("sbatch stderr:\n%s", result.stderr.decode(errors="replace"))
            return None
        return job_id

    def detect_job_id(self) -> str | None:
        """Return the Slurm job ID from the execution environment."""
        return getenv("SLURM_JOB_ID")


def slurm_generate_settings(scheduler_config: dict) -> str:
    """
    This function generate bash settings for Slurm job scheduler.

    :return: Generated settings.
    :rtype: str
    """
    # get log path and job scheduler config
    log_path = WRFRUN_NEW.config.get_log_path()

    # get scheduler configs
    stdout_log_path = f"{log_path}/slurm.log"
    stderr_log_path = f"{log_path}/slurm.err"
    node_num = scheduler_config["node_num"]
    queue_name = scheduler_config["queue_name"]
    core_num = get_core_num()

    template_path = WRFRUN_NEW.resource.get_package_resource(SCHEDULER_SLURM_TEMPLATE)
    with open(template_path, "r") as f:
        template = f.read()

    return template.format(
        STDOUT_LOG_PATH=stdout_log_path,
        STDERR_LOG_PATH=stderr_log_path,
        CORE_NUM=core_num,
        NODE_NUM=node_num,
        QUEUE_NAME=queue_name,
    )


__all__ = ["SlurmBackend", "slurm_generate_settings"]
