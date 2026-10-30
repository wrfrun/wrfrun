"""
wrfrun.scheduler.pbs
####################

Scheduler interface for PBS system.

.. autosummary::
    :toctree: generated/

    PBSBackend
    pbs_generate_settings
"""

import logging
import re
from os import getenv
from pathlib import Path

from wrfrun.core import WRFRUN_NEW, call_subprocess
from wrfrun.res import SCHEDULER_PBS_TEMPLATE

from .utils import get_core_num

LOGGER = logging.getLogger("wrfrun")


class PBSBackend:
    """Submit and identify PBS jobs."""

    name = "pbs"

    def submit(self, script_path: Path) -> str | None:
        """Submit ``script_path`` through ``qsub`` and return its job ID."""
        result = call_subprocess(["qsub", str(script_path)])
        job_id = result.stdout.decode(errors="replace").strip()
        if re.fullmatch(r"\d+(?:\[[^]]+\])?(?:\.[\w.-]+)?", job_id) is None:
            LOGGER.warning("Could not read PBS job ID from qsub output. Check whether the task was submitted.")
            LOGGER.warning("qsub stdout:\n%s", result.stdout.decode(errors="replace"))
            if result.stderr:
                LOGGER.warning("qsub stderr:\n%s", result.stderr.decode(errors="replace"))
            return None
        return job_id

    def detect_job_id(self) -> str | None:
        """Return the PBS job ID from the execution environment."""
        return getenv("PBS_JOBID")


def pbs_generate_settings(scheduler_config: dict) -> str:
    """
    This function generate bash settings for PBS job scheduler.

    :return: Generated settings.
    :rtype: str
    """
    # get log path and job scheduler config
    log_path = WRFRUN_NEW.config.get_log_path()

    # get scheduler configs
    stdout_log_path = f"{log_path}/pbs.log"
    stderr_log_path = f"{log_path}/pbs.err"
    node_num = scheduler_config["node_num"]
    queue_name = scheduler_config["queue_name"]
    core_num = get_core_num()

    template_path = WRFRUN_NEW.resource.get_package_resource(SCHEDULER_PBS_TEMPLATE)
    with open(template_path, "r") as f:
        template = f.read()

    return template.format(
        STDOUT_LOG_PATH=stdout_log_path,
        STDERR_LOG_PATH=stderr_log_path,
        NODE_NUM=node_num,
        CORE_NUM=core_num,
        QUEUE_NAME=queue_name,
    )


__all__ = ["PBSBackend", "pbs_generate_settings"]
