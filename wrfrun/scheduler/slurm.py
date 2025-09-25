"""
wrfrun.scheduler.slurm
######################

Scheduler interface for Slurm system.

.. autosummary::
    :toctree: generated/

    slurm_generate_settings
"""

from wrfrun.core import WRFRUNConfig
from wrfrun.res import SCHEDULER_SLURM_TEMPLATE
from .utils import get_core_num


def slurm_generate_settings(scheduler_config: dict) -> str:
    """
    This function generate bash settings for Slurm job scheduler.

    :return: Generated settings.
    :rtype: str
    """
    # get log path and job scheduler config
    log_path = WRFRUNConfig.get_log_path()

    # get scheduler configs
    stdout_log_path = f"{log_path}/slurm.log"
    stderr_log_path = f"{log_path}/slurm.err"
    node_num = scheduler_config["node_num"]
    queue_name = scheduler_config["queue_name"]
    core_num = get_core_num()

    template_path = WRFRUNConfig.parse_resource_uri(SCHEDULER_SLURM_TEMPLATE)
    with open(template_path, "r") as f:
        template = f.read()

    return template.format(
        STDOUT_LOG_PATH=stdout_log_path,
        STDERR_LOG_PATH=stderr_log_path,
        CORE_NUM=core_num,
        NODE_NUM=node_num,
        QUEUE_NAME=queue_name,
    )


__all__ = ["slurm_generate_settings"]
