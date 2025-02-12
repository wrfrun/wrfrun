from os import environ
from os.path import exists, dirname, abspath

from .core import WRFRUNConfig
from .res import PBS_SCRIPT_TEMPLATE
from .utils import logger


def prepare_pbs_script(main_file_path: str):
    """Prepare the bash script to be submitted to PBS work system.

    Args:
        main_file_path (str): The path of main Python file.
    """
    # check main file
    if not exists(main_file_path):
        logger.error(f"Wrong path of main Python file: {main_file_path}")
        raise FileNotFoundError

    # get absolute path of parent directory
    dir_path = abspath(dirname(main_file_path))

    # read log path and PBS setting from config
    log_path = WRFRUNConfig.get_log_path()
    PBS_setting = WRFRUNConfig.get_pbs_config()

    # set PBS log path
    stdout_log_path = f"{log_path}/PBS.log"
    stderr_log_path = f"{log_path}/PBS.log"

    # set environment parameter
    env_settings = ''
    if len(PBS_setting["env_settings"]) != 0:
        for key in PBS_setting["env_settings"]:
            env_settings += f"{key}={PBS_setting['env_settings'][key]}\n"

    # set command
    exec_cmd = f"{PBS_setting['python_interpreter']} {main_file_path}"

    # read template and write to file
    with open(f"{dir_path}/run.sh", "w") as f:

        with open(PBS_SCRIPT_TEMPLATE, "r") as f_template:
            template = f_template.read()

        template = template.format(
            STDOUT_LOG_PATH=stdout_log_path,
            STDERR_LOG_PATH=stderr_log_path,
            NODE_NUM=PBS_setting["node_num"],
            CORE_NUM=PBS_setting["core_num"],
            ENV_SETTINGS=env_settings,
            WORK_PATH=dir_path,
            WORK_COMMAND=exec_cmd
        )

        f.write(template)

    logger.info(
        f"PBS script has been generated and write to file {dir_path}/run.sh. Check it and submit it to PBS system to run wrfrun.")


def get_core_num() -> int:
    """Read core num from config.

    Returns:
        int: Core number.
    """
    return WRFRUNConfig.get_pbs_config()["core_num"]


def in_pbs() -> bool:
    """Check if we're in a PBS work.

    Returns:
        bool: True if we're in, False is we aren't.
    """
    # check if we're a PBS task
    if "PBS_ENVIRONMENT" in environ:
        # we're in a PBS task
        return True
    else:
        return False


__all__ = ["prepare_pbs_script", "get_core_num", "in_pbs"]
