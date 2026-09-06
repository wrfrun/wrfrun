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

from os.path import abspath, exists
from pathlib import Path
from pprint import pformat

from wrfrun.core import WRFRUN_NEW, NamelistError, NamelistIDError
from wrfrun.log import logger

from ...core.type import ResourceRef


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
    if not exists(file_path):
        logger.error(f"Can't find config file: '{file_path}'")
        raise FileNotFoundError(f"Can't find config file: '{file_path}'")

    palm_config = parse_palm_config(file_path)

    if not WRFRUN_NEW.namelist.check_namelist_id("palm_config"):
        if not WRFRUN_NEW.namelist.register_namelist_id("palm_config"):
            logger.error("Failed to register namelist id 'palm_config'.")
            raise NamelistIDError("Failed to register namelist id 'palm_config'.")

    WRFRUN_NEW.namelist.read_namelist(palm_config, "palm_config")


def write_palm_config(file_path: str | Path | ResourceRef):
    """
    Write PALM config to a file.

    :param file_path: Target file path.
    :type file_path: str | Path | ResourceRef
    :raises NamelistError: PALM config isn't read.
    """
    if not WRFRUN_NEW.namelist.check_namelist_id("palm_config"):
        logger.error("You haven't read PALM config yet.")
        raise NamelistError("You haven't read PALM config yet.")

    palm_config = WRFRUN_NEW.namelist.get_namelist("palm_config")

    if isinstance(file_path, ResourceRef):
        _file_path = WRFRUN_NEW.resource.get_custom_resource(file_path)
    else:
        _file_path = Path(file_path)

    if exists(file_path):
        backup_file_path = _file_path.parent / "backup.palm.config"

        WRFRUN_NEW.io.move(
            {
                "file_path": _file_path,
                "save_path": backup_file_path,
                "is_data": False,
                "is_output": False,
            }
        )

        logger.warning(f"Old file is backuped to '{backup_file_path}'")

    with open(_file_path, "w") as f:
        for key in palm_config:
            if key == "others":
                # write later
                continue

            f.write(f"%{key} {palm_config[key]}\n")

        for _settings in palm_config["others"]:
            f.write(f"{_settings}\n")


def prepare_palm_config(workspace_root: ResourceRef):
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
    root_path = WRFRUN_NEW.resource.get_custom_resource(workspace_root).as_posix()
    default_values = {
        "base_directory": root_path,
        "base_data": f"{root_path}/job",
        "user_source_path": f"{root_path}/job/$run_identifier/USER_CODE",
        "fast_io_catalog": f"{root_path}/tmp",
        "restart_data_path": f"{root_path}/tmp",
        "output_data_path": f"{root_path}/job",
        "local_jobcatalog": f"{root_path}/job/$run_identifier/LOG_FILES",
    }

    loaded_config = WRFRUN_NEW.namelist.get_namelist("palm_config")
    update_values = {x: default_values[x] for x in default_values if x in loaded_config}

    logger.info(
        f"The following new settings are applied to make PALM works in wrfrun workspace:\n{pformat(update_values, indent=4)}"
    )
    WRFRUN_NEW.namelist.update_namelist(update_values, "palm_config")


__all__ = ["parse_palm_config", "read_palm_config", "write_palm_config", "prepare_palm_config"]
