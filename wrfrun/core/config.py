"""
This file contains functions to read the config file of wrfrun
"""

import yaml
from copy import deepcopy
from os.path import exists
from shutil import copyfile
from typing import Union, Tuple

from wrfrun.res import CONFIG_TEMPLATE
from wrfrun.utils import logger


class _Config:
    def __init__(self):
        self._config = {}

    def load_config(self, config_path: Union[str, None] = None):
        """Load config

        Args:
            config_path (Union[str, None], optional): YAML config file. Defaults to None.
        """
        # check the config file
        if config_path is not None:
            # check if it exists
            if not exists(config_path):
                logger.error(
                    f"Config file doesn't exist, copy template config to {config_path}")
                logger.error(f"Please modify it.")
                # copy the template file to config_path
                copyfile(CONFIG_TEMPLATE, config_path)
                raise FileNotFoundError(config_path)
        else:
            logger.info(f"Read config template since you doesn't give config file")
            logger.info(
                f"A new config file has been saved to ./config.yaml, you can change and use it latter")
            # copy template to config_path
            copyfile(CONFIG_TEMPLATE, "./config.yaml")
            config_path = "./config.yaml"

        # read template
        with open(config_path, "r") as f:
            self._config = yaml.load(f, Loader=yaml.FullLoader)

    def save_config(self, save_path: str):
        """Save config to a file.

        Args:
            save_path (str): File path of the config.
        """
        with open(save_path, "w") as f:
            yaml.dump(self._config, f, Dumper=yaml.Dumper)

    def __getitem__(self, item):
        if len(self._config) == 0:
            logger.error(f"Attempt to read value before load config. Load config by using `load_config`")
            raise RuntimeError(f"Attempt to read value before load config. Load config by using `load_config`")

        return deepcopy(self._config[item])

    def get_wrf_config(self) -> dict:
        """
        Return the config of WRF.

        :return: A dict object.
        :rtype: dict
        """
        return deepcopy(self["wrf"])

    def get_log_path(self) -> str:
        """
        Return the save path of logs.

        :return: A directory path.
        :rtype: str
        """
        return self["wrfrun"]["log_path"]

    def get_socket_server_config(self) -> Tuple[str, int]:
        """
        Return settings of the socket server.

        :return: ("host", port)
        :rtype: tuple
        """
        return self["wrfrun"]["socket_host"], self["wrfrun"]["socket_port"]

    def get_pbs_config(self) -> dict:
        """
        Return the config of PBS work system.

        :return: A dict object.
        :rtype: dict
        """
        return deepcopy(self["wrfrun"]["PBS"])

    def get_output_path(self) -> str:
        """
        Return the output path, in which all results will be placed.

        :return: A directory path.
        :rtype: str
        """
        return self["wrfrun"]["output_path"]


WRFRUNConfig = _Config()


def load_config(config_path: Union[str, None] = None):
    """Load config

    Args:
        config_path (Union[str, None], optional): YAML config file. Defaults to None.

    Returns:
        dict: Config
    """
    global WRFRUNConfig
    WRFRUNConfig.load_config(config_path)


def save_config(save_path: str):
    """Save config to a file.

    Args:
        save_path (str): File path of the config.
    """
    global WRFRUNConfig
    WRFRUNConfig.save_config(save_path)


__all__ = ["load_config", "save_config", "WRFRUNConfig"]
