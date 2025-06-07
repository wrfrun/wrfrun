"""
This file contains functions to read the config file of wrfrun
"""

from copy import deepcopy
from os import environ, makedirs
from os.path import abspath, basename, dirname, exists
from shutil import copyfile
from typing import Optional, Tuple, Union

import f90nml
import tomli
import tomli_w

from .error import ResourceURIError, WRFRunContextError, ModelNameError
from ..utils import logger


class _WRFRunResources:
    """
    Manage resource files used by wrfrun components.
    These resources include various configuration files from NWP as well as those provided by wrfrun itself.
    Since their actual file paths may vary depending on the wrfrun installation environment, wrfrun maps them using URIs to ensure consistent access regardless of the environment.
    """
    def __init__(self):
        self._resource_namespace_db = {}

    def check_resource_uri(self, unique_uri: str) -> bool:
        """
        Check if the uri has been registered.

        :param unique_uri: Unique URI represents the resource.
        :type unique_uri: str
        :return: True or False.
        :rtype: bool
        """
        if unique_uri in self._resource_namespace_db:
            return True

        else:
            return False

    def register_resource_uri(self, unique_uri: str, res_space_path: str):
        """
        This function should only be used by wrfrun functions.

        Register a unique resource file namespace.

        :param unique_uri: Unique URI represents the resource. It must start with ``:WRFRUN_`` and end with ``:``. For example, ``":WRFRUN_WORK_PATH:"``.
        :type unique_uri: str
        :param res_space_path: REAL absolute path of your resource path. For example, "$HOME/.config/wrfrun/res".
        :type res_space_path: str
        :return:
        :rtype:
        """
        if not (unique_uri.startswith(":WRFRUN_") and unique_uri.endswith(":")):
            logger.error(f"Can't register resource URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")
            raise ResourceURIError(f"Can't register resource URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")

        if unique_uri in self._resource_namespace_db:
            logger.error(f"Resource URI '{unique_uri}' exists.")
            raise ResourceURIError(f"Resource URI '{unique_uri}' exists.")



        logger.debug(f"Register URI '{unique_uri}' to '{res_space_path}'")
        self._resource_namespace_db[unique_uri] = res_space_path

    def parse_resource_uri(self, file_path: str) -> str:
        """
        Return a real file path by parsing the URI string in it.

        Normal path will be returned with no change.

        :param file_path: File path string which may contain URI string.
        :type file_path: str
        :return: Real file path.
        :rtype: str
        """
        if not file_path.startswith(":WRFRUN_"):
            return file_path

        res_namespace_string = file_path.split(":")[1]
        res_namespace_string = f":{res_namespace_string}:"

        if res_namespace_string in self._resource_namespace_db:
            file_path = file_path.replace(res_namespace_string, self._resource_namespace_db[res_namespace_string])

            if not file_path.startswith(":WRFRUN_"):
                return file_path

            else:
                return self.parse_resource_uri(file_path)

        else:
            logger.error(f"Unknown resource URI: '{res_namespace_string}'")
            raise ResourceURIError(f"Unknown resource URI: '{res_namespace_string}'")


class _WRFRunConstants:
    """
    Define all variables that will be used by other wrfrun components.
    These variables are related to the wrfrun installation environment and configuration files.
    They are defined either directly or mapped using URIs to ensure consistent access across all components.
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
        self._WRFRUN_REPLAY_WORK_PATH = f"{self._WRFRUN_HOME_PATH}/replay"

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
        self.USE_WRFDA: bool = False

        # output directory of ungrib
        self._UNGRIB_OUT_DIR = "./outputs"

        self._WRFRUN_OUTPUT_PATH = ":WRFRUN_OUTPUT_PATH:"
        self._WRFRUN_RESOURCE_PATH = ":WRFRUN_RESOURCE_PATH:"

        self.IS_IN_REPLAY = False

        self.IS_RECORDING = False

        # in this mode, wrfrun will do all things except call the numerical model.
        # all output rules will also not be executed.
        self.FAKE_SIMULATION_MODE = False

    def _get_uri_map(self) -> dict[str, str]:
        """
        Return uri and its value.
        We will use this to register uri when initialize config.

        :return:
        :rtype:
        """
        return {
            self.WRFRUN_TEMP_PATH: self._WRFRUN_TEMP_PATH,
            self.WRFRUN_HOME_PATH: self._WRFRUN_HOME_PATH,
            self.WRFRUN_WORKSPACE_PATH: self._WORK_PATH,
            self.WPS_WORK_PATH: self._WPS_WORK_PATH,
            self.WRF_WORK_PATH: self._WRF_WORK_PATH,
            self.WRFDA_WORK_PATH: self._WRFDA_WORK_PATH,
            self.WRFRUN_REPLAY_WORK_PATH: self._WRFRUN_REPLAY_WORK_PATH,
        }

    @property
    def WRFRUN_REPLAY_WORK_PATH(self) -> str:
        return ":WRFRUN_REPLAY_WORK_PATH:"

    @property
    def WRFRUN_TEMP_PATH(self) -> str:
        """
        Path of the directory storing temporary files.

        :return: Path of the directory storing temporary files.
        :rtype: str
        """
        return ":WRFRUN_TEMP_PATH:"

    @property
    def WRFRUN_HOME_PATH(self) -> str:
        """
        Path of the directory storing wrfrun config files.

        :return: Path of the directory storing temporary files.
        :rtype: str
        """
        return ":WRFRUN_HOME_PATH:"

    @property
    def WRFRUN_WORKSPACE_PATH(self) -> str:
        """
        Path of the wrfrun workspace.

        :return: Path of the wrfrun workspace.
        :rtype: str
        """
        return ":WRFRUN_WORK_PATH:"

    @property
    def WPS_WORK_PATH(self) -> str:
        """
        Path of the directory to run WPS.

        :return: Path of the directory to run WPS.
        :rtype: str
        """
        return ":WRFRUN_WPS_WORK_PATH:"

    @property
    def WRF_WORK_PATH(self) -> str:
        """
        Path of the directory to run WRF.

        :return: Path of the directory to run WRF.
        :rtype: str
        """
        return ":WRFRUN_WRF_WORK_PATH:"

    @property
    def WRFDA_WORK_PATH(self) -> str:
        """
        Path of the directory to run WRFDA.

        :return: Path of the directory to run WRFDA.
        :rtype: str
        """
        return ":WRFRUN_WRFDA_WORK_PATH:"

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

    @property
    def WRFRUN_OUTPUT_PATH(self) -> str:
        """
        A marco string represents the save path of output files in wrfrun config.
        """
        return self._WRFRUN_OUTPUT_PATH

    @property
    def WRFRUN_RESOURCE_PATH(self) -> str:
        """
        Return the preserved string used by wrfrun resource files.
        """
        return self._WRFRUN_RESOURCE_PATH

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
        self._namelist_dict = {}
        self._namelist_id_list = ("param", "geog_static_data", "wps", "wrf", "wrfda")

    def register_custom_namelist_id(self, namelist_id: str) -> bool:
        """
        Register a namelist with a unique id so you can read, update and write it later.

        :param namelist_id: A unique namelist id.
        :type namelist_id: str
        :return: True if register successfully, else False.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list:
            return False

        else:
            self._namelist_id_list += (namelist_id,)
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
        if namelist_id not in self._namelist_id_list:
            return

        self.delete_namelist(namelist_id)
        self._namelist_id_list = tuple(set(self._namelist_id_list) - {namelist_id, })

    def check_namelist_id(self, namelist_id: str) -> bool:
        """
        Check if a namelist id is registered.

        :param namelist_id: Unique namelist ID.
        :type namelist_id: Unique namelist ID.
        :return: True if the ID is registered, else False.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list:
            return True
        else:
            return False

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

        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")

        self._namelist_dict[namelist_id] = f90nml.read(file_path).todict()

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
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")

        if namelist_id not in self._namelist_dict:
            logger.error(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
            raise KeyError(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")

        f90nml.Namelist(self._namelist_dict[namelist_id]).write(save_path, force=overwrite)

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
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")

        elif namelist_id not in self._namelist_dict:
            self._namelist_dict[namelist_id] = new_values
            return

        else:
            reference = self._namelist_dict[namelist_id]

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
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")
        elif namelist_id not in self._namelist_dict:
            return {}
        else:
            return deepcopy(self._namelist_dict[namelist_id])

    def delete_namelist(self, namelist_id: str):
        """
        Delete specified namelist values.

        :param namelist_id: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other id you have registered.
        :type namelist_id: str
        :return:
        :rtype:
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")

        if namelist_id not in self._namelist_dict:
            return

        self._namelist_dict.pop(namelist_id)


class WRFRunConfig(_WRFRunConstants, _WRFRunNamelist, _WRFRunResources):
    """
    Class to manage wrfrun config.
    """
    _instance = None
    _initialized = False

    def __init__(self):
        if self._initialized:
            return

        _WRFRunConstants.__init__(self)
        _WRFRunNamelist.__init__(self)
        _WRFRunResources.__init__(self)

        self._config = {}

        # register uri for wrfrun constants
        for key, value in self._get_uri_map().items():
            self.register_resource_uri(key, value)

        self._config_template_file_path = None

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def set_config_template_path(self, file_path: str):
        """
        Set the path of template file.

        :param file_path: Template file path.
        :type file_path: str
        :return:
        :rtype:
        """
        self._config_template_file_path = file_path

    def load_wrfrun_config(self, config_path: Optional[str] = None):
        """
        Load wrfrun config.

        :param config_path: YAML config file. Defaults to None.
        :type config_path: str
        """
        config_template_path = self.parse_resource_uri(self._config_template_file_path)

        if config_path is not None:
            if not exists(config_path):
                logger.error(f"Config file doesn't exist, copy template config to {config_path}")
                logger.error("Please modify it.")

                if not exists(dirname(config_path)):
                    makedirs(dirname(config_path))

                copyfile(config_template_path, config_path)
                raise FileNotFoundError(config_path)
        else:
            logger.info("Read config template since you doesn't give config file")
            logger.info("A new config file has been saved to './config.toml', you can change and use it latter")

            copyfile(config_template_path, "./config.toml")
            config_path = "./config.toml"

        with open(config_path, "rb") as f:
            self._config = tomli.load(f)

        # register URI for output directory.
        output_path = abspath(self["output_path"])
        self.register_resource_uri(self.WRFRUN_OUTPUT_PATH, output_path)

    def save_wrfrun_config(self, save_path: str):
        """
        Save config to a file.

        :param save_path: Save path of the config.
        :type save_path: str
        """
        save_path = self.parse_resource_uri(save_path)

        path_dir = dirname(save_path)
        if not exists(path_dir):
            makedirs(path_dir)

        with open(save_path, "wb") as f:
            tomli_w.dump(self._config, f)

    def __getitem__(self, item):
        if len(self._config) == 0:
            logger.error("Attempt to read value before load config")
            raise RuntimeError("Attempt to read value before load config")

        return deepcopy(self._config[item])

    def get_input_data_path(self) -> list[str]:
        """
        Return the path of input data.

        :return: Path list.
        :rtype: list
        """
        return deepcopy(self["input_data_path"])

    def get_model_config(self, model_name: str) -> dict:
        """
        Return the config of a NWP model.

        :param model_name: Name of the model. For example, "wrf".
        :type model_name: str
        :return: A dict object.
        :rtype: dict
        """
        if model_name not in self["model"]:
            logger.error(f"Config of model '{model_name}' isn't found in your config file.")
            raise ModelNameError(f"Config of model '{model_name}' isn't found in your config file.")

        return deepcopy(self["model"][model_name])

    def get_log_path(self) -> str:
        """
        Return the save path of logs.

        :return: A directory path.
        :rtype: str
        """
        return self["log_path"]

    def get_socket_server_config(self) -> Tuple[str, int]:
        """
        Return settings of the socket server.

        :return: ("host", port)
        :rtype: tuple
        """
        return self["server_host"], self["server_port"]

    def get_job_scheduler_config(self) -> dict:
        """
        Return the config of job scheduler.

        :return: A dict object.
        :rtype: dict
        """
        return deepcopy(self["job_scheduler"])

    def get_core_num(self) -> int:
        """
        Return the number of CPU cores.
        :return:
        :rtype:
        """
        return self["core_num"]

    def get_ungrib_out_dir_path(self) -> str:
        """
        Get the output directory of ungrib output (WRF intermediate file).

        :return: URI path.
        :rtype: str
        """
        wif_prefix = self.get_namelist("wps")["ungrib"]["prefix"]
        wif_path = f"{self.WPS_WORK_PATH}/{dirname(wif_prefix)}"

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

    def write_namelist(self, save_path: str, namelist_id: str, overwrite=True):
        save_path = self.parse_resource_uri(save_path)
        super().write_namelist(save_path, namelist_id, overwrite)


WRFRUNConfig = WRFRunConfig()


__all__ = ["WRFRUNConfig"]
