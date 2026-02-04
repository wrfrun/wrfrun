"""
wrfrun.model.wrf.log
####################

Functions to parse and clear WPS/WRF model logs.

.. autosummary::
    :toctree: generated/

    get_wrf_simulated_seconds
    clear_wrf_logs
"""

import subprocess
from datetime import datetime
from os import listdir
from os.path import exists
from shutil import move
from typing import Optional

from wrfrun.core import WRFRUN
from wrfrun.log import logger
from wrfrun.utils import check_path
from wrfrun.workspace.wrf import get_wrf_workspace_path


def get_wrf_simulated_seconds(start_datetime: datetime, log_file_path: Optional[str] = None) -> int:
    """
    Read the latest line of WRF's log file and calculate how many seconds WRF has integrated.

    :param start_datetime: WRF start datetime.
    :type start_datetime: datetime
    :param log_file_path: Absolute path of the log file to be parsed.
    :type log_file_path: str
    :return: Integrated seconds. If this method fails to calculate the time, the returned value is ``-1``.
    :rtype: int
    """
    # use linux cmd to get the latest line of wrf log files
    if log_file_path is None:
        log_file_path = WRFRUN.config.parse_resource_uri(f"{get_wrf_workspace_path('wrf')}/rsl.out.0000")
    res = subprocess.run(["tail", "-n", "1", log_file_path], capture_output=True)
    log_text = res.stdout.decode()

    if not (log_text.startswith("d01") or log_text.startswith("d02")):
        return -1

    time_string = log_text.split()[1]

    try:
        current_datetime = datetime.strptime(time_string, "%Y-%m-%d_%H:%M:%S")
        # remove timezone info so we can calculate.
        date_delta = current_datetime - start_datetime.replace(tzinfo=None)
        seconds = date_delta.days * 24 * 60 * 60 + date_delta.seconds

    except ValueError:
        seconds = -1

    return seconds


def clear_wrf_logs() -> None:
    """
    Collect unsaved WPS/WRF log files and save them to the corresponding
    output directory of the ``Executable``.
    """
    WRFRUNConfig = WRFRUN.config

    # wps
    work_path = WRFRUNConfig.parse_resource_uri(get_wrf_workspace_path("wps"))

    if exists(work_path):
        log_files = [x for x in listdir(work_path) if x.endswith(".log")]

        if len(log_files) > 0:
            logger.warning("Found unprocessed log files of WPS model.")

            log_save_path = f"{WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)}/wps_unsaved_logs"
            check_path(log_save_path)

            for _file in log_files:
                move(f"{work_path}/{_file}", f"{log_save_path}/{_file}")

            logger.warning(f"Unprocessed log files of WPS model has been saved to {log_save_path}, check it")

    # wrf
    work_path = WRFRUNConfig.parse_resource_uri(get_wrf_workspace_path("wrf"))

    if exists(work_path):
        log_files = [x for x in listdir(work_path) if x.startswith("rsl.")]

        if len(log_files) > 0:
            logger.warning("Found unprocessed log files of WRF model.")

            log_save_path = f"{WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)}/wrf_unsaved_logs"
            check_path(log_save_path)

            for _file in log_files:
                move(f"{work_path}/{_file}", f"{log_save_path}/{_file}")

            logger.warning(f"Unprocessed log files of WRF model has been saved to {log_save_path}, check it")


__all__ = ["get_wrf_simulated_seconds", "clear_wrf_logs"]
