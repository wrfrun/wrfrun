"""
wrfrun.model.palm.config
########################

Process config file of PALM.

.. autosummary::
    toctree: generated/

    parse_palm_config
    read_palm_config
    write_palm_config
    prepare_palm_config
"""

from os import remove
from os.path import abspath, dirname, exists
from pprint import pformat
from shutil import move

from wrfrun.core import WRFRUN_NEW, NamelistError, NamelistIDError
from wrfrun.log import logger
from wrfrun.workspace.palm import get_palm_workspace_path


def parse_palm_config(config_file_path: str) -> dict:
    """
    Parse stupid palm config file.

    :param config_file_path: PALM config file path.
    :type config_file_path: str
    :raises ValueError: PALM config file not found.
    :return: A dictionary that stores PALM config,
             with environmental variables are stored as key-value pair,
             and other settings stored in a list named "others".
    :rtype: dict
    """
    res = {"others": []}

    if not exists(config_file_path):
        logger.error(f"PALM config file '{config_file_path}' not found.")
        raise ValueError(f"PALM config file '{config_file_path}' not found.")

    # Read stupid config file line by line
    with open(config_file_path, "r") as f:
        for _line in f:
            if _line.startswith("#") or _line == "":
                continue

            elif not _line.startswith("%"):
                res["others"].append(_line)

            else:
                args = _line.split(" ")
                args = [x for x in args if x != ""]
                key = args[0][1:]  # remove leading %
                value = " ".join(args[1:])
                res[key] = value

    return res


def read_palm_config(file_path: str):
    """
    Read PALM config file.

    :raises NamelistIDError: Failed to register namelist id "palm_config".
    """
    WRFRUNConfig = WRFRUN_NEW.config

    if not exists(file_path):
        logger.error(f"Can't find config file: '{file_path}'")
        raise FileNotFoundError(f"Can't find config file: '{file_path}'")

    palm_config = parse_palm_config(file_path)

    if not WRFRUNConfig.check_namelist_id("palm_config"):
        if not WRFRUNConfig.register_namelist_id("palm_config"):
            logger.error("Failed to register namelist id 'palm_config'.")
            raise NamelistIDError("Failed to register namelist id 'palm_config'.")

    WRFRUNConfig.read_namelist(palm_config, "palm_config")


def write_palm_config(file_path: str):
    """
    Write PALM config to a file.

    :param file_path: Target file path.
    :type file_path: str
    :raises NamelistError: PALM config isn't read.
    """
    WRFRUNConfig = WRFRUN_NEW.config

    if not WRFRUNConfig.check_namelist_id("palm_config"):
        logger.error("You haven't read PALM config yet.")
        raise NamelistError("You haven't read PALM config yet.")

    palm_config = WRFRUNConfig.get_namelist("palm_config")
    file_path = WRFRUNConfig.parse_resource_uri(file_path)

    if exists(file_path):
        backup_file_path = f"{dirname(file_path)}/backup.palm.config"

        if exists(backup_file_path):
            remove(backup_file_path)
            logger.warning("Old backup is deleted.")

        move(file_path, backup_file_path)
        logger.warning(f"Old file is backuped to '{backup_file_path}'")

    with open(file_path, "w") as f:
        for key in palm_config:
            if key == "others":
                # write later
                continue

            f.write(f"%{key} {palm_config[key]}\n")

        for _settings in palm_config["others"]:
            f.write(f"{_settings}\n")


def prepare_palm_config():
    """
    Read and process PALM configs.
    """
    WRFRUNConfig = WRFRUN_NEW.config

    model_config = WRFRUNConfig.get_model_config("palm")
    palm_path = abspath(model_config["palm_path"])
    config_file_path = model_config["config_file_path"]

    if config_file_path == "":
        if not exists(f"{palm_path}/.palm.config.default"):
            logger.error(f"Can't find the default config file: '{palm_path}/.palm.config.default', please provide one.")
            raise FileNotFoundError(
                f"Can't find the default config file: '{palm_path}/.palm.config.default', please provide one."
            )

        read_palm_config(f"{palm_path}/.palm.config.default")

    else:
        read_palm_config(config_file_path)

    # change environmental variables
    root_path = WRFRUNConfig.parse_resource_uri(get_palm_workspace_path())
    default_values = {
        "base_directory": root_path,
        "base_data": f"{root_path}/job",
        "user_source_path": f"{root_path}/job/$run_identifier/USER_CODE",
        "fast_io_catalog": f"{root_path}/tmp",
        "restart_data_path": f"{root_path}/tmp",
        "output_data_path": f"{root_path}/job",
        "local_jobcatalog": f"{root_path}/job/$run_identifier/LOG_FILES",
    }

    loaded_config = WRFRUNConfig.get_namelist("palm_config")
    update_values = {x: default_values[x] for x in default_values if x in loaded_config}

    logger.info(
        f"The following new settings are applied to make PALM works in wrfrun workspace:\n{pformat(update_values, indent=4)}"
    )
    WRFRUNConfig.update_namelist(update_values, "palm_config")


__all__ = ["parse_palm_config", "read_palm_config", "write_palm_config", "prepare_palm_config"]
