"""
wrfrun.scheduler.lsf
####################

Scheduler interface for LSF system.

.. autosummary::
    :toctree: generated/

    lsf_generate_settings
"""

from wrfrun.core import WRFRUNConfig
from wrfrun.res import SCHEDULER_LSF_TEMPLATE
from .utils import get_core_num


def lsf_generate_settings(scheduler_config: dict) -> str:
    """
    This function generate bash settings for LSF job scheduler.

    :return: Generated settings.
    :rtype: str
    """
    # get log path and job scheduler config
    log_path = WRFRUNConfig.get_log_path()

    # get scheduler configs
    stdout_log_path = f"{log_path}/lsf.log"
    stderr_log_path = f"{log_path}/lsf.err"
    node_num = scheduler_config["node_num"]
    queue_name = scheduler_config["queue_name"]
    core_num = get_core_num()

    template_path = WRFRUNConfig.parse_resource_uri(SCHEDULER_LSF_TEMPLATE)
    with open(template_path, "r") as f:
        template = f.read()

    return template.format(
        STDOUT_LOG_PATH=stdout_log_path,
        STDERR_LOG_PATH=stderr_log_path,
        CORE_NUM=core_num * node_num,
        QUEUE_NAME=queue_name,
    )


__all__ = ["lsf_generate_settings"]
