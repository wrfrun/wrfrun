"""
wrfrun.core._config
###################

.. autosummary::
    :toctree: generated/

    WRFRunConfig

WRFRunConfig
************

This class inherits :class:`NamelistMixIn <wrfrun.core._namelist.NamelistMixIn>`
and :class:`DebugMixIn <wrfrun.core._debug.DebugMixIn>`.
URI registration and resolution are delegated to
:class:`WRFRUNURI <wrfrun.core.uri.WRFRUNURI>`; use ``WRFRUN.uri`` for new code.

Besides the methods from its parents, :class:`WRFRunConfig` provides methods to read and access user config files.
Its URI methods remain compatibility interfaces.
"""

from copy import deepcopy
from os import makedirs
from os.path import abspath, dirname, exists
from shutil import copyfile
from typing import Callable, Optional, Tuple

import tomli
import tomli_w

from ..log import logger
from ._namelist import NamelistMixIn
from .error import ModelNameError, WRFRunContextError
from .session._debug import DebugMixIn
from .uri import WRFRUNURI


class WRFRunConfig(NamelistMixIn, DebugMixIn):
    """
    Comprehensive class to manage wrfrun config, runtime constants, namelists and resource files.
    """

    def __init__(self, uri_manager: WRFRUNURI):
        """

        :param work_dir: ``wrfrun`` work directory path.
        :type work_dir: str
        """
        self._URI_manager = uri_manager

        super().__init__(uri_parse_func=self._URI_manager.parse_resource_uri)

        self._config = {}

        self._config_template_file_path = None

        # record context status
        self._WRFRUN_CONTEXT_STATUS = False
        # record WRF progress status
        self._WRFRUN_WORK_STATUS = ""

        self.IS_IN_REPLAY: bool = False
        self.IS_RECORDING: bool = False

        # in this mode, wrfrun will do all things except call the numerical model.
        # all output rules will also not be executed.
        self.FAKE_SIMULATION_MODE = False

        self._register_wrfrun_uris()

    def apply_register_func(self, func_list: list[Callable[["WRFRunConfig"], None]]):
        """
        Call register functions provided by other submodules.

        :param func_list: A list contains register functions.
        :type func_list: list[Callable[["WRFRunConfig"], None]]
        """
        while len(func_list) != 0:
            _func = func_list.pop(0)
            _func(self)

    @classmethod
    def from_config_file(
        cls, uri_manager: WRFRUNURI, config_file: str, register_funcs: list[Callable[["WRFRunConfig"], None]]
    ) -> "WRFRunConfig":
        """
        Read the config file and create a instance.

        :param config_file: Config file path.
        :type config_file: str
        :param register_funcs: Register function list.
        :type register_funcs: list[Callable[["WRFRunConfig"], None]]
        :return: New instance
        :rtype: WRFRunConfig
        """
        instance = cls(uri_manager)
        instance.apply_register_func(register_funcs)
        instance.load_wrfrun_config(config_file)

        return instance

    def _register_wrfrun_uris(self):
        for key, value in self._URI_manager._get_uri_map().items():
            self.register_resource_uri(key, value)

    def set_config_template_path(self, file_path: str):
        """
        Set file path of the config template file.

        ``WRFRunConfig`` needs to know

        :param file_path: Template file path.
        :type file_path: str
        """
        self._config_template_file_path = file_path

    def load_wrfrun_config(self, config_path: str):
        """
        Load configs from a config file.

        If the config path is invalid, ``WRFRunConfig`` will create a new config file at the same place,
        and raise :class:`FileNotFoundError`.

        :param config_path: TOML config file.
        :type config_path: str
        """
        config_template_path = self.parse_resource_uri(self._config_template_file_path)

        if not exists(config_path):
            logger.error(f"Config file doesn't exist, copy template config to {config_path}")
            logger.error("Please modify it.")

            if not exists(dirname(config_path)):
                makedirs(dirname(config_path))

            copyfile(config_template_path, config_path)
            raise FileNotFoundError(config_path)

        with open(config_path, "rb") as f:
            self._config = tomli.load(f)

        config_dir_path = abspath(dirname(config_path))

        # merge model config.
        keys_list = list(self._config["model"].keys())
        for model_key in keys_list:
            # skip the key that isn't model.
            if model_key == "debug_level":
                continue

            if "include" not in self._config["model"][model_key]:
                continue

            # use = True, and have "include" key
            if self._config["model"][model_key]["use"]:
                include_file = self._config["model"][model_key]["include"]
                if include_file[0] != "/":
                    include_file = f"{config_dir_path}/{include_file}"

                with open(include_file, "rb") as f:
                    # keep "use" key, as other components may use this key
                    _mode_config = tomli.load(f)
                    _mode_config.update({"use": True})
                    self._config["model"][model_key] = _mode_config

            else:
                self._config["model"].pop(model_key)

        # register URI for output directory.
        output_path = abspath(self["output_path"])
        self.unregister_resource_uri(self._URI_manager.WRFRUN_OUTPUT_PATH)
        self.register_resource_uri(self._URI_manager.WRFRUN_OUTPUT_PATH, output_path)

        # some additional check
        if self._config["input_data_path"] == "":
            logger.warning("It seems you forget to set 'input_data_path', set it to 'data'.")
            self._config["input_data_path"] = "data"

    def save_wrfrun_config(self, save_path: str):
        """
        Save wrfrun config to a file.

        :param save_path: Save path of the config.
        :type save_path: str
        """
        save_path = self.parse_resource_uri(save_path)

        path_dir = dirname(save_path)
        if not exists(path_dir):
            makedirs(path_dir)

        with open(save_path, "wb") as f:
            tomli_w.dump(self._config, f)

    def __getitem__(self, item: str):
        """
        You can access wrfrun config like the way to access values in a dictionary.

        For example:

        >>> from wrfrun.core import WRFRUN
        >>> model_config = WRFRUN.config["model"]    # get all model configs.

        :param item: Keys.
        :type item: str
        """
        if len(self._config) == 0:
            logger.error("Attempt to read value before load config")
            raise RuntimeError("Attempt to read value before load config")

        return deepcopy(self._config[item])

    def __setitem__(self, key: str, value):
        if key == "model":
            logger.error("Use `update_model_config` to change model configurations.")
            raise KeyError("Use `update_model_config` to change model configurations.")

        if key in self._config:
            self._config[key] = value

        else:
            logger.error(f"Can't find key '{key}' in your config.")
            raise KeyError(f"Can't find key '{key}' in your config.")

    def get_input_data_path(self, model_name: Optional[str] = None) -> str:
        """
        Get the path of directory in which stores the input data.

        :param model_name: ``Executable`` name, defaults to None. If None, return the root path.
        :type model_name: Optional[str]
        :return: Directory path.
        :rtype: str
        """
        root_path = deepcopy(self["input_data_path"])

        if model_name is None:
            return root_path
        else:
            return f"{root_path}/{model_name}"

    def get_model_config(self, model_name: str) -> dict:
        """
        Get the config of a NWP model.

        An exception :class:`ModelNameError <wrfrun.core.error.ModelNameError>` will be raised
        if the config can't be found.

        :param model_name: Name of the model. For example, ``wrf``.
        :type model_name: str
        :return: A dictionary.
        :rtype: dict
        """
        if model_name not in self["model"]:
            logger.error(f"Config of model '{model_name}' isn't found in your config file.")
            raise ModelNameError(f"Config of model '{model_name}' isn't found in your config file.")

        return self["model"][model_name]

    def update_model_config(self, model_name: str, value: dict):
        """
        Update the config of a NWP model.

        An exception :class:`ModelNameError <wrfrun.core.error.ModelNameError>` will be raised
        if the config can't be found.

        :param model_name: Name of the model. For example, ``wrf``.
        :type model_name: str
        :param value: Dictionary contains new values.
        :type value: dict
        """
        if model_name not in self["model"]:
            logger.error(f"Config of model '{model_name}' isn't found in your config file.")
            raise ModelNameError(f"Config of model '{model_name}' isn't found in your config file.")

        self._config["model"][model_name].update(value)

    def get_log_path(self) -> str:
        """
        Get the directory path to save logs.

        :return: A directory path.
        :rtype: str
        """
        return self["log_path"]

    def get_socket_server_config(self) -> Tuple[str, int]:
        """
        Get settings of the socket server.

        :return: ("host", port)
        :rtype: tuple
        """
        return self["server_host"], self["server_port"]

    def get_job_scheduler_config(self) -> dict:
        """
        Get configs of job scheduler.

        :return: A dict object.
        :rtype: dict
        """
        return deepcopy(self["job_scheduler"])

    def get_core_num(self) -> int:
        """
        Get the number of CPU cores to be used.
        :return: Core numbers
        :rtype: int
        """
        return self["core_num"]

    def write_namelist(self, save_path: str, namelist_id: str, overwrite=True):
        """
        Write namelist values of a ``namelist_id`` to a file.
        This method is overwritten to convert URIs in ``save_path`` first.

        :param save_path: Target file path.
        :type save_path: str
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :param overwrite: If overwrite the existed file.
        :type overwrite: bool
        """
        save_path = self.parse_resource_uri(save_path)
        super().write_namelist(save_path, namelist_id, overwrite)

    def check_wrfrun_context(self, error=False) -> bool:
        """
        Check if in WRFRun context or not.

        :param error: An exception :class:`WRFRunContextError` will be raised
                      if ``error==True`` when we are not in WRFRun context.
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

        :param status: ``True`` or ``False``.
        :type status: bool
        """
        self._WRFRUN_CONTEXT_STATUS = status

    @property
    def WRFRUN_WORK_STATUS(self) -> str:
        """
        ``wrfrun`` work status.

        This attribute can be changed by ``Executable`` to reflect the current work progress of ``wrfrun``.
        The returned string is the name of ``Executable``.

        :return: A string reflect the current work progress.
        :rtype: str
        """
        return self._WRFRUN_WORK_STATUS

    @WRFRUN_WORK_STATUS.setter
    def WRFRUN_WORK_STATUS(self, value: str):
        """
        Set ``wrfrun`` work status.

        ``wrfrun`` recommends ``Executable`` set the status string with their name,
        so to avoid the possible conflicts with other ``Executable``,
        and the user can easily understand the current work progress.

        :param value: A string represents the work status.
        :type value: str
        """
        self._WRFRUN_WORK_STATUS = value

    def check_resource_uri(self, unique_uri: str) -> bool:
        return self._URI_manager.check_resource_uri(unique_uri)

    def register_resource_uri(self, unique_uri: str, res_space_path: str):
        return self._URI_manager.register_resource_uri(unique_uri, res_space_path)

    def unregister_resource_uri(self, unique_uri: str):
        return self._URI_manager.unregister_resource_uri(unique_uri)

    def parse_resource_uri(self, resource_path: str) -> str:
        return self._URI_manager.parse_resource_uri(resource_path)


__all__ = ["WRFRunConfig"]
