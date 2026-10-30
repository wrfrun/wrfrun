"""
wrfrun.scheduler.lsf
####################

Scheduler interface for LSF system.

.. autosummary::
    :toctree: generated/

    LSFBackend
    lsf_generate_settings
"""

import logging
import re
from os import getenv
from pathlib import Path

from wrfrun.core import WRFRUN_NEW, call_subprocess
from wrfrun.res import SCHEDULER_LSF_TEMPLATE

from .utils import get_core_num

LOGGER = logging.getLogger("wrfrun")


class LSFBackend:
    """Submit and identify LSF jobs."""

    name = "lsf"

    def submit(self, script_path: Path) -> str | None:
        """Submit ``script_path`` through ``bsub`` and return its job ID."""
        result = call_subprocess(["bsub"], stdin_path=str(script_path))
        output = result.stdout.decode(errors="replace")
        match = re.search(r"Job <([^>]+)>", output)
        if match is None:
            LOGGER.warning("Could not read LSF job ID from bsub output. Check whether the task was submitted.")
            LOGGER.warning("bsub stdout:\n%s", output)
            if result.stderr:
                LOGGER.warning("bsub stderr:\n%s", result.stderr.decode(errors="replace"))
            return None
        return match.group(1)

    def detect_job_id(self) -> str | None:
        """Return the LSF job ID from the execution environment."""
        return getenv("LSB_JOBID")


def lsf_generate_settings(scheduler_config: dict) -> str:
    """
    This function generate bash settings for LSF job scheduler.

    :return: Generated settings.
    :rtype: str
    """
    # get log path and job scheduler config
    log_path = WRFRUN_NEW.config.get_log_path()

    # get scheduler configs
    stdout_log_path = f"{log_path}/lsf.log"
    stderr_log_path = f"{log_path}/lsf.err"
    node_num = scheduler_config["node_num"]
    queue_name = scheduler_config["queue_name"]
    core_num = get_core_num()

    template_path = WRFRUN_NEW.resource.get_package_resource(SCHEDULER_LSF_TEMPLATE)
    with open(template_path, "r") as f:
        template = f.read()

    return template.format(
        STDOUT_LOG_PATH=stdout_log_path,
        STDERR_LOG_PATH=stderr_log_path,
        CORE_NUM=core_num * node_num,
        QUEUE_NAME=queue_name,
    )


__all__ = ["LSFBackend", "lsf_generate_settings"]
