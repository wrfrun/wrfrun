import subprocess
from datetime import datetime
from typing import Optional

from wrfrun import WRFRUNConfig
from wrfrun.workspace.wrf import WORKSPACE_MODEL_WRF


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
        log_file_path = WRFRUNConfig.parse_resource_uri(f"{WORKSPACE_MODEL_WRF}/rsl.out.0000")
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


__all__ = ["get_wrf_simulated_seconds"]
