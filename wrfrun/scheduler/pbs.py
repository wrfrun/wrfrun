"""
wrfrun.scheduler.pbs
####################

Scheduler interface for PBS system.

.. autosummary::
    :toctree: generated/

    pbs_generate_settings
"""

from wrfrun.core import get_wrfrun_config
from wrfrun.res import SCHEDULER_PBS_TEMPLATE
from .utils import get_core_num


def pbs_generate_settings(scheduler_config: dict) -> str:
    """
    This function generate bash settings for PBS job scheduler.

    :return: Generated settings.
    :rtype: str
    """
    WRFRUNConfig = get_wrfrun_config()

    # get log path and job scheduler config
    log_path = WRFRUNConfig.get_log_path()

    # get scheduler configs
    stdout_log_path = f"{log_path}/pbs.log"
    stderr_log_path = f"{log_path}/pbs.err"
    node_num = scheduler_config["node_num"]
    queue_name = scheduler_config["queue_name"]
    core_num = get_core_num()

    template_path = WRFRUNConfig.parse_resource_uri(SCHEDULER_PBS_TEMPLATE)
    with open(template_path, "r") as f:
        template = f.read()

    return template.format(
        STDOUT_LOG_PATH=stdout_log_path,
        STDERR_LOG_PATH=stderr_log_path,
        NODE_NUM=node_num,
        CORE_NUM=core_num,
        QUEUE_NAME=queue_name,
    )


__all__ = ["pbs_generate_settings"]
