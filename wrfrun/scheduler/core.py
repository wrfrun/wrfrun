"""
wrfrun.scheduler.core
#####################

Functions to interact with job scheduler.

.. autosummary::
    :toctree: generated/

    submit_scheduler_task
    prepare_scheduler_script
"""

import logging
import re
import sys
from os.path import abspath, dirname, exists
from shlex import join, quote

from wrfrun.core import WRFRUN_NEW, call_subprocess
from wrfrun.res import RUN_SH_TEMPLATE

from .lsf import lsf_generate_settings
from .pbs import pbs_generate_settings
from .slurm import slurm_generate_settings

LOGGER = logging.getLogger("wrfrun")

ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ENVIRONMENT_MARKER = "# wrfrun:environment"
COMMAND_MARKER = "# wrfrun:command"


def submit_scheduler_task(main_file_path: str):
    """
    Prepare the bash script for scheduler and submit it.

    :param main_file_path: Path of the main entry Python file.
    :type main_file_path: str
    """
    script_path = prepare_scheduler_script(main_file_path)

    scheduler_name = WRFRUN_NEW.config.get_job_scheduler_config()["job_scheduler"]

    match scheduler_name:
        case "pbs":
            submit_command = ["qsub", script_path]

        case "slurm":
            submit_command = ["sbatch", script_path]

        case "lsf":
            submit_command = ["bsub"]

        case _:
            LOGGER.error(f"Unknown scheduler name: {scheduler_name}")
            raise ValueError(f"Unknown scheduler name: {scheduler_name}")

    LOGGER.info(f"Submit scheduler task with backend '{scheduler_name}'.")

    if scheduler_name == "lsf":
        call_subprocess(submit_command, stdin_path=script_path)
    else:
        call_subprocess(submit_command)


def prepare_scheduler_script(main_file_path: str) -> str:
    """
    Prepare the bash script to be submitted to job scheduler.

    :param main_file_path: Path of the main entry file.
    :type main_file_path: str
    :return: Absolute path of generated shell script.
    :rtype: str
    """
    # check main file path
    if not exists(main_file_path):
        LOGGER.error(f"Wrong path of main entry file: {main_file_path}")
        raise FileNotFoundError(f"Wrong path of main entry file: {main_file_path}")

    # get absolute path of main entry file's parent directory
    dir_path = abspath(dirname(main_file_path))

    scheduler_configs = WRFRUN_NEW.config.get_job_scheduler_config()

    # generate environment settings
    env_settings = "export WRFRUN_ENV_JOB_SCHEDULER=1\n"
    env_settings += f"export WRFRUN_EXPERIMENT={quote(WRFRUN_NEW.layout.experiment)}\n"
    env_settings += f"export WRFRUN_RUN_ID={quote(WRFRUN_NEW.layout.run_id)}\n"
    if len(scheduler_configs["env_settings"]) > 0:
        for key in scheduler_configs["env_settings"]:
            if not ENV_KEY_PATTERN.fullmatch(key):
                LOGGER.error(f"Invalid environment variable name: {key}")
                raise ValueError(f"Invalid environment variable name: {key}")

            value = str(scheduler_configs["env_settings"][key])
            env_settings += f"export {key}={quote(value)}\n"

    # generate command
    python_interpreter = scheduler_configs["python_interpreter"] or sys.executable
    exec_cmd = join([python_interpreter, main_file_path])

    LOGGER.debug(f"Start command in scheduler: {exec_cmd}")

    experiment_template_path = WRFRUN_NEW.resource.get_custom_resource(
        WRFRUN_NEW.resource.CONFIG_DIR / f"experiments/{WRFRUN_NEW.layout.experiment}/scheduler/submit.sh"
    )
    template_path = experiment_template_path
    if not template_path.is_file():
        template_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.CONFIG_DIR / "scheduler/submit.sh")

    if template_path.is_file():
        template = template_path.read_text()
        if template.count(ENVIRONMENT_MARKER) != 1 or template.count(COMMAND_MARKER) != 1:
            raise ValueError(f"Custom scheduler template must contain {ENVIRONMENT_MARKER} and {COMMAND_MARKER} once each.")

        template = template.replace(ENVIRONMENT_MARKER, env_settings.rstrip())
        template = template.replace(COMMAND_MARKER, f"cd {quote(dir_path)}\nexec {exec_cmd}")
    else:
        match scheduler_configs["job_scheduler"]:
            case "lsf":
                scheduler_settings = lsf_generate_settings(scheduler_configs)

            case "pbs":
                scheduler_settings = pbs_generate_settings(scheduler_configs)

            case "slurm":
                scheduler_settings = slurm_generate_settings(scheduler_configs)

            case _:
                LOGGER.error(f"Unknown scheduler name: {scheduler_configs['job_scheduler']}")
                raise ValueError(f"Unknown scheduler name: {scheduler_configs['job_scheduler']}")

        shell_template_path = WRFRUN_NEW.resource.get_package_resource(RUN_SH_TEMPLATE)
        template = shell_template_path.read_text().format(
            SCHEDULER_SETTINGS=scheduler_settings,
            ENV_SETTINGS=env_settings,
            WORK_COMMAND=exec_cmd,
            WORK_PATH=quote(dir_path),
        )

    script_path = WRFRUN_NEW.layout.workspace_dir.parent / "submit.sh"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(template)

    LOGGER.info(f"Job scheduler script written to {script_path}")

    return str(script_path)


__all__ = ["prepare_scheduler_script", "submit_scheduler_task"]
