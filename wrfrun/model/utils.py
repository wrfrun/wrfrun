from os import listdir
from shutil import move

from ..core import WRFRUNConfig
from ..utils import check_path, logger


def clear_model_logs():
    """
    This function can automatically collect WRF log files and save them to ``output_path``.
    This function is used inside the wrfrun package.
    If you want to do something about the log files, check the corresponding code of interface functions in ``wrfrun.model.run``.

    :return:
    :rtype:
    """
    work_status = WRFRUNConfig.WRFRUN_WORK_STATUS
    work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRF_WORK_PATH)

    log_files = [x for x in listdir(work_path) if x.startswith("rsl.")]

    if len(log_files) > 0:
        logger.warning(f"Found unprocessed log files of {work_status}")

        log_save_path = f"{WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_OUTPUT_PATH)}/{work_status}/logs"
        check_path(log_save_path)

        for _file in log_files:
            move(f"{work_path}/{_file}", f"{log_save_path}/{_file}")

        logger.warning(f"Unprocessed log files of {work_status} has been saved to {log_save_path}, check it")


__all__ = ["clear_model_logs"]
