"""
wrfrun.model.utils
##################

Utility functions used by models.

.. autosummary::
    :toctree: generated/

    clear_model_logs
"""

from os import listdir
from shutil import move

from ..core import get_wrfrun_config
from ..utils import check_path, logger
from ..workspace.wrf import get_wrf_workspace_path


def clear_model_logs():
    """
    This function can automatically collect unsaved log files,
    and save them to the corresponding output directory of the ``Executable``.
    """
    WRFRUNConfig = get_wrfrun_config()
    work_status = WRFRUNConfig.WRFRUN_WORK_STATUS
    work_path = WRFRUNConfig.parse_resource_uri(get_wrf_workspace_path("wrf"))

    log_files = [x for x in listdir(work_path) if x.startswith("rsl.") or x.endswith(".log")]

    if len(log_files) > 0:
        logger.warning(f"Found unprocessed log files of {work_status}")

        log_save_path = f"{WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)}/{work_status}/logs"
        check_path(log_save_path)

        for _file in log_files:
            move(f"{work_path}/{_file}", f"{log_save_path}/{_file}")

        logger.warning(f"Unprocessed log files of {work_status} has been saved to {log_save_path}, check it")


__all__ = ["clear_model_logs"]
