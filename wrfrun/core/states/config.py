"""
wrfrun.core.states.config
#########################

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

import logging
from copy import deepcopy
from pathlib import Path
from typing import Optional, Tuple

import tomli

from ..error import ModelNameError
from ..runtime.io import IOService
from ..runtime.resource import ResourceCatalog, ResourceRef

LOGGER = logging.getLogger("wrfrun")


class ConfigService:
    """
    Comprehensive class to manage wrfrun config, runtime constants, namelists and resource files.
    """

    def __init__(self, io: IOService, resource: ResourceCatalog):
        """

        :param work_dir: ``wrfrun`` work directory path.
        :type work_dir: str
        """
        self._io = io
        self._resource = resource

        self._config = {}

        self._config_template_file_path = self._resource.CORE_RESOURCE / "config/config.template.toml"

    @classmethod
    def from_config_file(
        cls,
        config_file: str,
        io: IOService,
        resource: ResourceCatalog,
    ) -> "ConfigService":
        """
        Read the config file and create a instance.

        :param config_file: Config file path.
        :type config_file: str
        :param io: IO service.
        :type io: IOService
        :param resource: Resource manager.
        :type resource: ResourceCatalog
        :return: New instance
        :rtype: WRFRunConfig
        """
        instance = cls(io, resource)
        instance.load_wrfrun_config(config_file)

        return instance

    def load_wrfrun_config(self, config_path: str):
        """
        Load configs from a config file.

        If the config path is invalid, ``WRFRunConfig`` will create a new config file at the same place,
        and raise :class:`FileNotFoundError`.

        :param config_path: TOML config file.
        :type config_path: str
        """
        config_file = Path(config_path).resolve()

        if not config_file.is_file():
            LOGGER.error(f"Config file doesn't exist, copy template config to {config_file}")
            LOGGER.error("Please modify it.")

            config_file.parent.mkdir(exist_ok=True)

            self._io.copy(
                file_path=self._config_template_file_path,
                save_path=config_file,
            )

            raise FileNotFoundError(config_file)

        with open(config_file, "rb") as f:
            self._config = tomli.load(f)

        project_root_path = config_file.parent

        # register provider before load model's plugin
        input_path = Path(self["input_data_path"]).resolve()
        output_path = Path(self["output_path"]).resolve()
        work_dir = Path(self["work_dir"]).resolve()
        log_dir = Path(self["log_path"]).resolve()
        template_dir = Path(self["template_dir"]).resolve()
        self._resource.register_provider("output", output_path)
        self._resource.register_provider("project", project_root_path)
        self._resource.register_provider("input", input_path)
        self._resource.register_provider("workspace", work_dir / "workspace")
        self._resource.register_provider("temp", work_dir / "temp")
        self._resource.register_provider("replay", work_dir / "replay")
        self._resource.register_provider("log", log_dir)
        self._resource.register_provider("template", template_dir)

        from wrfrun.model.plugins import load_model_plugin

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
                    include_file = f"{project_root_path}/{include_file}"

                with open(include_file, "rb") as f:
                    # keep "use" key, as other components may use this key
                    _mode_config = tomli.load(f)
                    _mode_config.update({"use": True})
                    self._config["model"][model_key] = _mode_config

                load_model_plugin(model_key).register()

            else:
                self._config["model"].pop(model_key)

        # some additional check
        if self._config["input_data_path"] == "":
            LOGGER.error(
                "It is not recommanded to place your data in project root dir. "
                "Change [magenta]input_data_path[/magenta] to another location."
            )
            raise ValueError(
                "It is not recommanded to place your data in project root dir. Change input_data_path to another location."
            )

    def save_wrfrun_config(self, save_path: str | ResourceRef):
        """
        Save wrfrun config to a file.

        :param save_path: Save path of the config file.
        :type save_path: str | ResourceRef
        """
        self._io.write_toml(self._config, save_path)

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
            LOGGER.error("Attempt to read value before load config")
            raise RuntimeError("Attempt to read value before load config")

        return deepcopy(self._config[item])

    def __setitem__(self, key: str, value):
        """
        You can change wrfrun config like the way to change values in a dictionary,
        except changing model configs.

        You should use :py:meth:`update_model_config` to change model configs.

        For example:

        >>> from wrfrun.core import WRFRUN
        >>> model_config = WRFRUN.config["model"]    # get all model configs.

        :param item: Keys.
        :type item: str
        """
        if key == "model":
            LOGGER.error("Use `update_model_config` to change model configurations.")
            raise KeyError("Use `update_model_config` to change model configurations.")

        if key in self._config:
            self._config[key] = value

        else:
            LOGGER.error(f"Can't find key '{key}' in your config.")
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
            LOGGER.error(f"Config of model '{model_name}' isn't found in your config file.")
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
            LOGGER.error(f"Config of model '{model_name}' isn't found in your config file.")
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


__all__ = ["ConfigService"]
