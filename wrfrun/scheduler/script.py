from os.path import exists, abspath, dirname

from wrfrun import WRFRUNConfig
from wrfrun.res import RUN_SH_TEMPLATE
from wrfrun.utils import logger
from .lsf import lsf_generate_settings
from .pbs import pbs_generate_settings
from .slurm import slurm_generate_settings


def prepare_scheduler_script(main_file_path: str):
    """
    Prepare the bash script to be submitted to job scheduler.

    :param main_file_path: Path of the main entry file.
    :type main_file_path: str
    """
    # check main file path
    if not exists(main_file_path):
        logger.error(f"Wrong path of main entry file: {main_file_path}")
        raise FileNotFoundError(f"Wrong path of main entry file: {main_file_path}")

    # get absolute path of main entry file's parent directory
    dir_path = abspath(dirname(main_file_path))

    scheduler_configs = WRFRUNConfig.get_job_scheduler_config()

    # generate scheduler settings
    match scheduler_configs["job_scheduler"]:
        case "lsf":
            scheduler_settings = lsf_generate_settings(scheduler_configs)

        case "pbs":
            scheduler_settings = pbs_generate_settings(scheduler_configs)

        case "slurm":
            scheduler_settings = slurm_generate_settings(scheduler_configs)

        case _:
            logger.error(f"Unknown scheduler name: {scheduler_configs['job_scheduler']}")
            raise ValueError(f"Unknown scheduler name: {scheduler_configs['job_scheduler']}")

    # generate environment settings
    env_settings = 'export WRFRUN_ENV_JOB_SCHEDULER=1\n'
    if len(scheduler_configs["env_settings"]) > 0:
        for key in scheduler_configs["env_settings"]:
            env_settings += f"export {key}={scheduler_configs['env_settings'][key]}\n"

    # generate command
    exec_cmd = f"{scheduler_configs['python_interpreter']} {main_file_path}"

    # generate shell script
    shell_template_path = WRFRUNConfig.parse_resource_uri(RUN_SH_TEMPLATE)
    with open(f"{dir_path}/run.sh", "w") as f:

        with open(shell_template_path, "r") as f_template:
            template = f_template.read()

        template = template.format(
            SCHEDULER_SETTINGS=scheduler_settings,
            ENV_SETTINGS=env_settings,
            WORK_COMMAND=exec_cmd,
        )

        f.write(template)

    logger.info(f"Job scheduler script written to {dir_path}/run.sh")


__all__ = ["prepare_scheduler_script"]
