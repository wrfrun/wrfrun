"""
This file contains functions to read the config file of wrfrun
"""

from copy import deepcopy
from os import environ, makedirs
from os.path import abspath, basename, dirname, exists
from shutil import copyfile
from typing import Optional, Tuple, Union

import f90nml
import yaml

from .error import WRFRunContextError
from ..res import CONFIG_TEMPLATE
from ..utils import logger


class _WRFRunConstants:
    """
    Define some variables used by wrfrun.
    """
    def __init__(self):
        # the path we may need to store temp files,
        # don't worry, it will be deleted once the system reboots
        self._WRFRUN_TEMP_PATH = "/tmp/wrfrun"

        # WRF may need a large disk space to store output, we can't run wrf in /tmp,
        # so we will create a folder in $HOME/.config to run wrf.
        # we need to check if we're running as a root user
        USER_HOME_PATH = f"{environ['HOME']}"
        if USER_HOME_PATH in ["/", "/root", ""]:
            logger.warning(f"User's home path is '{USER_HOME_PATH}', which means you are running this program as a root user")
            logger.warning("It's not recommended to use wrfrun as a root user")
            logger.warning("Set USER_HOME_PATH as /root")
            USER_HOME_PATH = "/root"

        self._WRFRUN_HOME_PATH = f"{USER_HOME_PATH}/.config/wrfrun"

        # work path to run WPS, WRF and WRFDA
        self._WORK_PATH = f"{self._WRFRUN_HOME_PATH}/workspace"
        self._WPS_WORK_PATH = f"{self._WORK_PATH}/WPS"
        self._WRF_WORK_PATH = f"{self._WORK_PATH}/WRF"
        self._WRFDA_WORK_PATH = f"{self._WORK_PATH}/WRFDA"

        # record WRF progress status
        self._WORK_STATUS = ""

        # record context status
        self._WRFRUN_CONTEXT_STATUS = False

        # WRFDA is not necessary
        self._USE_WRFDA: bool = False

        # output directory of ungrib
        self._UNGRIB_OUT_DIR = "./outputs"

    @property
    def WRFRUN_TEMP_PATH(self) -> str:
        """
        Path of the directory storing temporary files.

        :return: Path of the directory storing temporary files.
        :rtype: str
        """
        return self._WRFRUN_TEMP_PATH

    @property
    def WRFRUN_HOME_PATH(self) -> str:
        """
        Path of the directory storing wrfrun config files.

        :return: Path of the directory storing temporary files.
        :rtype: str
        """
        return self._WRFRUN_HOME_PATH

    @property
    def WRFRUN_WORKSPACE_PATH(self) -> str:
        """
        Path of the wrfrun workspace.

        :return: Path of the wrfrun workspace.
        :rtype: str
        """
        return self._WORK_PATH

    @property
    def WPS_WORK_PATH(self) -> str:
        """
        Path of the directory to run WPS.

        :return: Path of the directory to run WPS.
        :rtype: str
        """
        return self._WPS_WORK_PATH

    @property
    def WRF_WORK_PATH(self) -> str:
        """
        Path of the directory to run WRF.

        :return: Path of the directory to run WRF.
        :rtype: str
        """
        return self._WRF_WORK_PATH

    @property
    def WRFDA_WORK_PATH(self) -> str:
        """
        Path of the directory to run WRFDA.

        :return: Path of the directory to run WRFDA.
        :rtype: str
        """
        return self._WRFDA_WORK_PATH

    @property
    def WRFRUN_WORK_STATUS(self) -> str:
        """
        wrfrun work status.

        :return: wrfrun work status.
        :rtype: str
        """
        return self._WORK_STATUS

    @WRFRUN_WORK_STATUS.setter
    def WRFRUN_WORK_STATUS(self, value: str):
        if not isinstance(value, str):
            value = str(value)
        self._WORK_STATUS = value

    @property
    def UNGRIB_OUT_DIR(self):
        """
        Output directory path of ungrib.
        """
        return self._UNGRIB_OUT_DIR

    @UNGRIB_OUT_DIR.setter
    def UNGRIB_OUT_DIR(self, value: str):
        if not isinstance(value, str):
            value = str(value)
        self._UNGRIB_OUT_DIR = value

    def check_wrfrun_context(self, error=False) -> bool:
        """
        Check if we're in WRFRun context or not.

        :param error: Raise an error if ``error==True`` when we are not in WRFRun context.
        :type error: bool
        :return: True or False.
        :rtype: bool
        """
        if self._WRFRUN_CONTEXT_STATUS:
            return self._WRFRUN_CONTEXT_STATUS

        if not error:
            logger.warning("You are using wrfrun without entering `WRFRun` context, which may cause some functions don't work.")
            return self._WRFRUN_CONTEXT_STATUS

        logger.error("You need to enter `WRFRun` context to use wrfrun.")
        raise WRFRunContextError("You need to enter `WRFRun` context to use wrfrun.")

    def set_wrfrun_context(self, status: bool):
        """
        Change ``WRFRun`` context status to True or False.

        :param status: ``WRFRun`` context status.
        :type status: bool
        """
        self._WRFRUN_CONTEXT_STATUS = status


class _WRFRunNamelist:
    """
    A class to manage namelist config.
    """
    def __init__(self):
        self._wps_namelist = {}
        self._wrf_namelist = {}
        self._wrfda_namelist = {}
        self._custom_namelist = {}
        self._custom_namelist_type = ("param", "geog_static_data")

    def register_custom_namelist_id(self, namelist_id: str) -> bool:
        """
        Register a namelist with a unique id so you can read, update and write it later.

        :param namelist_id: A unique namelist id.
        :type namelist_id: str
        :return: True if register successfully, else False.
        :rtype: bool
        """
        if namelist_id in self._custom_namelist_type:
            return False

        else:
            self._custom_namelist_type += (namelist_id, )
            return True

    def unregister_custom_namelist_id(self, namelist_id: str):
        """
        Unregister a specified namelist id.
        If unregister successfully, all data about this namelist kind will be lost.

        :param namelist_id: A unique namelist id.
        :type namelist_id: str
        :return:
        :rtype:
        """
        if namelist_id not in self._custom_namelist_type:
            return

        self._custom_namelist_type = tuple(set(self._custom_namelist_type) - {namelist_id, })

    def read_namelist(self, file_path: str, namelist_id: str):
        """
        Read namelist.

        :param file_path: Namelist file path.
        :type file_path: str
        :param namelist_id: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other id you have registered.
        :type namelist_id: str
        """
        # check the file path
        if not exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError

        if namelist_id == "wps":
            self._wps_namelist = f90nml.read(file_path).todict()
        elif namelist_id == "wrf":
            self._wrf_namelist = f90nml.read(file_path).todict()
        elif namelist_id == "wrfda":
            self._wrfda_namelist = f90nml.read(file_path).todict()
        else:
            if namelist_id not in self._custom_namelist_type:
                logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
                raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")
            else:
                self._custom_namelist[namelist_id] = f90nml.read(file_path).todict()

    def write_namelist(self, save_path: str, namelist_id: str, overwrite=True):
        """
        Write namelist to file.

        :param save_path: Save path.
        :type save_path: str
        :param namelist_id: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other id you have registered.
        :type namelist_id: str
        :param overwrite: If overwrite the existed file, defaults to ``True``.
        :type overwrite: bool
        """
        if namelist_id == "wps":
            f90nml.Namelist(self._wps_namelist).write(save_path, force=overwrite)
        elif namelist_id == "wrf":
            f90nml.Namelist(self._wrf_namelist).write(save_path, force=overwrite)
        elif namelist_id == "wrfda":
            f90nml.Namelist(self._wrfda_namelist).write(save_path, force=overwrite)
        else:
            if namelist_id not in self._custom_namelist_type:
                logger.error(f"Unknown namelist type: {namelist_id}")
                raise ValueError(f"Unknown namelist type: {namelist_id}")

            if namelist_id not in self._custom_namelist:
                logger.error(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
                raise KeyError(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")

            f90nml.Namelist(self._custom_namelist[namelist_id]).write(save_path, force=overwrite)

    def update_namelist(self, new_values: Union[str, dict], namelist_id: str):
        """
        Update value in namelist data.

        You can give your custom namelist file, a whole namelist or a file only contains values you want to change.

        >>> namelist_file = "./namelist.wps"
        >>> WRFRUNConfig.update_namelist(namelist_file, namelist_id="wps")

        >>> namelist_file = "./namelist.wrf"
        >>> WRFRUNConfig.update_namelist(namelist_file, namelist_id="wrf")

        Or give a Dict object contains values you want to change.

        >>> namelist_values = {"ungrib": {"prefix": "./output/FILE"}}
        >>> WRFRUNConfig.update_namelist(namelist_values, namelist_id="wps")

        >>> namelist_values = {"time_control": {"debug_level": 100}}
        >>> WRFRUNConfig.update_namelist(namelist_values, namelist_id="wrf")

        :param new_values: New values.
        :type new_values: str | dict
        :param namelist_id: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other id you have registered.
        :type namelist_id: str
        """
        if namelist_id == "wps":
            reference = self._wps_namelist
        elif namelist_id == "wrf":
            reference = self._wrf_namelist
        elif namelist_id == "wrfda":
            reference = self._wrfda_namelist
        else:
            if namelist_id not in self._custom_namelist_type:
                logger.error(f"Unknown namelist type: {namelist_id}")
                raise ValueError(f"Unknown namelist type: {namelist_id}")
            elif namelist_id not in self._custom_namelist:
                self._custom_namelist[namelist_id] = new_values
                return
            else:
                reference = self._custom_namelist[namelist_id]

        if isinstance(new_values, str):
            if not exists(new_values):
                logger.error(f"File not found: {new_values}")
                raise FileNotFoundError(f"File not found: {new_values}")
            new_values = f90nml.read(new_values).todict()

        for key in new_values:
            if key in reference:
                reference[key].update(new_values[key])
            else:
                reference[key] = new_values[key]

    def get_namelist(self, namelist_id: str) -> dict:
        """
        Get specific namelist.

        :param namelist_id: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other id you have registered.
        :type namelist_id: str
        :return: Namelist.
        :rtype: dict
        """
        if namelist_id == "wps":
            return deepcopy(self._wps_namelist)
        elif namelist_id == "wrf":
            return deepcopy(self._wrf_namelist)
        elif namelist_id == "wrfda":
            return deepcopy(self._wrfda_namelist)
        else:
            if namelist_id not in self._custom_namelist_type:
                logger.error(f"Unknown namelist type: {namelist_id}")
                raise ValueError(f"Unknown namelist type: {namelist_id}")
            elif namelist_id not in self._custom_namelist:
                return {}
            else:
                return deepcopy(self._custom_namelist[namelist_id])

    def delete_namelist(self, namelist_id: str):
        """
        Delete specified namelist values.

        :param namelist_id: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other id you have registered.
        :type namelist_id: str
        :return:
        :rtype:
        """
        if namelist_id == "wps":
            self._wps_namelist = {}
        elif namelist_id == "wrf":
            self._wrf_namelist = {}
        elif namelist_id == "wrfda":
            self._wrfda_namelist = {}
        else:
            if namelist_id not in self._custom_namelist_type:
                logger.error(f"Unknown namelist type: {namelist_id}")
                raise ValueError(f"Unknown namelist type: {namelist_id}")

            if namelist_id not in self._custom_namelist:
                return

            self._custom_namelist.pop(namelist_id)


class WRFRunConfig(_WRFRunConstants, _WRFRunNamelist):
    """
    Class to manage wrfrun config.
    """
    _instance = None
    _initialized = False

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._config = {}

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def load_wrfrun_config(self, config_path: Optional[str] = None):
        """
        Load wrfrun config.

        :param config_path: YAML config file. Defaults to None.
        :type config_path: str
        """
        if config_path is not None:
            if not exists(config_path):
                logger.error(f"Config file doesn't exist, copy template config to {config_path}")
                logger.error("Please modify it.")

                if not exists(dirname(config_path)):
                    makedirs(dirname(config_path))

                copyfile(CONFIG_TEMPLATE, config_path)
                raise FileNotFoundError(config_path)
        else:
            logger.info("Read config template since you doesn't give config file")
            logger.info("A new config file has been saved to './config.yaml', you can change and use it latter")

            copyfile(CONFIG_TEMPLATE, "./config.yaml")
            config_path = "./config.yaml"

        with open(config_path, "r") as f:
            self._config = yaml.load(f, Loader=yaml.FullLoader)

    def save_wrfrun_config(self, save_path: str):
        """
        Save config to a file.

        :param save_path: File path of the config.
        :type save_path: str
        """
        with open(save_path, "w") as f:
            yaml.dump(self._config, f, Dumper=yaml.Dumper)

    def __getitem__(self, item):
        if len(self._config) == 0:
            logger.error("Attempt to read value before load config")
            raise RuntimeError("Attempt to read value before load config")

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

    def is_restart(self) -> bool:
        """
        Check if user does a restart run.

        :return:
        :rtype:
        """
        return self["wrf"]["restart"]

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

    def get_ungrib_out_dir_path(self) -> str:
        """
        Get the output directory of ungrib output (WRF intermediate file).

        :return: Absolute path.
        :rtype: str
        """
        wif_prefix = self.get_namelist("wps")["ungrib"]["prefix"]
        wif_path = abspath(f"{self.WPS_WORK_PATH}/{dirname(wif_prefix)}")

        return wif_path

    def get_ungrib_out_prefix(self) -> str:
        """
        Get the prefix string of ungrib output (WRF intermediate file).

        :return: Prefix string of ungrib output (WRF intermediate file).
        :rtype: str
        """
        wif_prefix = self.get_namelist("wps")["ungrib"]["prefix"]
        wif_prefix = basename(wif_prefix)
        return wif_prefix

    def set_ungrib_out_prefix(self, prefix: str):
        """
        Set the prefix string of ungrib output (WRF intermediate file).

        :param prefix: Prefix string of ungrib output (WRF intermediate file).
        :type prefix: str
        :return:
        :rtype:
        """
        self.update_namelist({
            "ungrib": {"prefix": f"{self.UNGRIB_OUT_DIR}/{prefix}"}
        }, "wps")

    def get_metgrid_fg_names(self) -> list[str]:
        """
        Get prefix strings from "fg_name" in namelist "metgrid" section.

        :return: Prefix strings list.
        :rtype: list
        """
        fg_names = self.get_namelist("wps")["metgrid"]["fg_name"]
        fg_names = [basename(x) for x in fg_names]
        return fg_names

    def set_metgrid_fg_names(self, prefix: Union[str, list[str]]):
        """
        Set prefix strings from "fg_name" in namelist "metgrid" section.

        :param prefix: Prefix strings list.
        :type prefix: str | list
        :return:
        :rtype:
        """
        if isinstance(prefix, str):
            prefix = [prefix, ]
        fg_names = [f"{self.UNGRIB_OUT_DIR}/{x}" for x in prefix]
        self.update_namelist({
            "metgrid": {"fg_name": fg_names}
        }, "wps")


WRFRUNConfig = WRFRunConfig()


__all__ = ["WRFRUNConfig", "WRFRunConfig"]
