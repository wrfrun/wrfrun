"""
wrfrun.core.config
##################

All classes in this module is used to manage various configurations of ``wrfrun`` and NWP model.

.. autosummary::
    :toctree: generated/

    WRFRunConfig
    _WRFRunConstants
    _WRFRunNamelist
    _WRFRunResources

WRFRunConfig
************

A comprehensive class which provides interfaces to access various configurations and resources.
It inherits from three classes: :class:`_WRFRunResources`, :class:`_WRFRunConstants` and :class:`_WRFRunNamelist`.
Users can use the global variable ``WRFRUNConfig``, which is the instance of this class being created when users import ``wrfrun``.
"""

from copy import deepcopy
from os import environ, makedirs
from os.path import abspath, dirname, exists
from shutil import copyfile
from sys import platform
from typing import Optional, Tuple, Union

import f90nml
import tomli
import tomli_w

from .error import ModelNameError, NamelistError, NamelistIDError, ResourceURIError, WRFRunContextError
from ..utils import logger


class _WRFRunResources:
    """
    Manage resource files used by wrfrun components
    """

    def __init__(self):
        """
        This class manage resource files used by wrfrun components.

        These resources include various configuration files from NWP as well as those provided by ``wrfrun`` itself.
        Since their actual file paths may vary depending on the installation environment,
        ``wrfrun`` maps them using URIs to ensure consistent access regardless of the environment.
        The URI always starts with the prefix string ``:WRFRUN_`` and ends with ``:``.

        To register custom URIs, user can use :meth:`_WRFRunResources.register_resource_uri`,
        which will check if the provided URI is valid.

        To convert any possible URIs in a string, user can use :meth:`_WRFRunResources.parse_resource_uri`

        For more information about how to use resource files, please see :class:`WRFRunConfig`,
        which inherits this class.
        """
        self._resource_namespace_db = {}

    def check_resource_uri(self, unique_uri: str) -> bool:
        """
        Check if the URI has been registered.

        ``wrfrun`` uses unique URIs to represent resource files. If you want to register a custom URI, you need to check if it's available.

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
        Register a resource path with a URI. The URI should start with ``:WRFRUN_`` ,end with ``:`` and hasn't been registered yet,
        otherwise an exception :class:`ResourceURIError` will be raised.

        :param unique_uri: Unique URI represents the resource. It must start with ``:WRFRUN_`` and end with ``:``. For example, ``":WRFRUN_WORK_PATH:"``.
        :type unique_uri: str
        :param res_space_path: REAL absolute path of your resource path. For example, "$HOME/.config/wrfrun/res".
        :type res_space_path: str
        """
        if not (unique_uri.startswith(":WRFRUN_") and unique_uri.endswith(":")):
            logger.error(f"Can't register resource URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")
            raise ResourceURIError(f"Can't register resource URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")

        if unique_uri in self._resource_namespace_db:
            logger.error(f"Resource URI '{unique_uri}' exists.")
            raise ResourceURIError(f"Resource URI '{unique_uri}' exists.")

        logger.debug(f"Register URI '{unique_uri}' to '{res_space_path}'")
        self._resource_namespace_db[unique_uri] = res_space_path

    def parse_resource_uri(self, resource_path: str) -> str:
        """
        Return the converted string by parsing the URI string in it.
        Normal path will be returned with no change.

        If the URI hasn't been registered, an exception :class:`ResourceURIError` will be raised.

        :param resource_path: Resource path string which may contain URI string.
        :type resource_path: str
        :return: Real resource path.
        :rtype: str

        For example, you can get the real path of ``wrfrun`` workspace with this method:

        >>> workspace_path = f"{WRFRUNConfig.WRFRUN_WORKSPACE_ROOT}/WPS"    # ":WRFRUN_WORKSPACE_PATH:/WPS"
        >>> real_path = WRFRUNConfig.parse_resource_uri(workspace_path)     # should be a valid path like: "/home/syize/.config/wrfrun/workspace/WPS"

        """
        if not resource_path.startswith(":WRFRUN_"):
            return resource_path

        res_namespace_string = resource_path.split(":")[1]
        res_namespace_string = f":{res_namespace_string}:"

        if res_namespace_string in self._resource_namespace_db:
            resource_path = resource_path.replace(res_namespace_string, self._resource_namespace_db[res_namespace_string])

            if not resource_path.startswith(":WRFRUN_"):
                return resource_path

            else:
                return self.parse_resource_uri(resource_path)

        else:
            logger.error(f"Unknown resource URI: '{res_namespace_string}'")
            raise ResourceURIError(f"Unknown resource URI: '{res_namespace_string}'")


class _WRFRunConstants:
    """
    Define all variables that will be used by other components.
    """

    def __init__(self):
        """
        Define all variables that will be used by other components.

        These variables are related to ``wrfrun`` installation environments, configuration files and more.
        They are defined either directly or mapped using URIs to ensure consistent access across all components.
        """
        # check system
        if platform != "linux":
            logger.debug(f"Not Linux system!")

            # set temporary dir path
            self._WRFRUN_TEMP_PATH = "./tmp/wrfrun"
            user_home_path = "./tmp/wrfrun"

        else:

            # the path we may need to store temp files,
            # don't worry, it will be deleted once the system reboots
            self._WRFRUN_TEMP_PATH = "/tmp/wrfrun"
            user_home_path = f"{environ['HOME']}"

        # WRF may need a large disk space to store output, we can't run wrf in /tmp,
        # so we will create a folder in $HOME/.config to run wrf.
        # we need to check if we're running as a root user
        if user_home_path in ["/", "/root", ""]:
            logger.warning(f"User's home path is '{user_home_path}', which means you are running this program as a root user")
            logger.warning("It's not recommended to use wrfrun as a root user")
            logger.warning("Set user_home_path as /root")
            user_home_path = "/root"

        self._WRFRUN_HOME_PATH = f"{user_home_path}/.config/wrfrun"
        # workspace root path
        self._WRFRUN_WORKSPACE_ROOT = f"{self._WRFRUN_HOME_PATH}/workspace"
        self._WRFRUN_WORKSPACE_MODEL = f"{self._WRFRUN_WORKSPACE_ROOT}/model"
        self._WRFRUN_WORKSPACE_REPLAY = f"{self._WRFRUN_WORKSPACE_ROOT}/replay"

        # record WRF progress status
        self._WRFRUN_WORK_STATUS = ""

        # record context status
        self._WRFRUN_CONTEXT_STATUS = False

        self._WRFRUN_OUTPUT_PATH = ":WRFRUN_OUTPUT_PATH:"
        self._WRFRUN_RESOURCE_PATH = ":WRFRUN_RESOURCE_PATH:"

        self.IS_IN_REPLAY = False

        self.IS_RECORDING = False

        # in this mode, wrfrun will do all things except call the numerical model.
        # all output rules will also not be executed.
        self.FAKE_SIMULATION_MODE = False

    def _get_uri_map(self) -> dict[str, str]:
        """
        Return URIs and their values.
        ``wrfrun`` will use this to register uri when initialize config.

        :return: A dict in which URIs are keys and their values are dictionary values.
        :rtype: dict
        """
        return {
            self.WRFRUN_TEMP_PATH: self._WRFRUN_TEMP_PATH,
            self.WRFRUN_HOME_PATH: self._WRFRUN_HOME_PATH,
            self.WRFRUN_WORKSPACE_ROOT: self._WRFRUN_WORKSPACE_ROOT,
            self.WRFRUN_WORKSPACE_MODEL: self._WRFRUN_WORKSPACE_MODEL,
            self.WRFRUN_WORKSPACE_REPLAY: self._WRFRUN_WORKSPACE_REPLAY,
        }

    @property
    def WRFRUN_WORKSPACE_REPLAY(self) -> str:
        """
        Path (URI) to store related files of ``wrfrun`` replay functionality.

        :return: URI.
        :rtype: str
        """
        return ":WRFRUN_WORKSPACE_REPLAY:"

    @property
    def WRFRUN_TEMP_PATH(self) -> str:
        """
        Path to store ``wrfrun`` temporary files.

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_TEMP_PATH:"

    @property
    def WRFRUN_HOME_PATH(self) -> str:
        """
        Root path of all others directories. .

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_HOME_PATH:"

    @property
    def WRFRUN_WORKSPACE_ROOT(self) -> str:
        """
        Path of the root workspace.

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_WORKSPACE_ROOT:"

    @property
    def WRFRUN_WORKSPACE_MODEL(self) -> str:
        """
        Path of the model workspace, in which ``wrfrun`` runs numerical models.

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_WORKSPACE_MODEL:"

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
        so to avoid the possible conflicts with other ``Executable`` and the user can easily understand the current work progress.

        :param value: A string represents the work status.
        :type value: str
        """
        if not isinstance(value, str):
            value = str(value)
        self._WRFRUN_WORK_STATUS = value

    @property
    def WRFRUN_OUTPUT_PATH(self) -> str:
        """
        The root path to store all outputs of the ``wrfrun`` and NWP model.

        :return: URI
        :rtype: str
        """
        return self._WRFRUN_OUTPUT_PATH

    @property
    def WRFRUN_RESOURCE_PATH(self) -> str:
        """
        The root path of all ``wrfrun`` resource files.

        :return: URI
        :rtype: str
        """
        return self._WRFRUN_RESOURCE_PATH

    def check_wrfrun_context(self, error=False) -> bool:
        """
        Check if in WRFRun context or not.

        :param error: An exception :class:`WRFRunContextError` will be raised if ``error==True`` when we are not in WRFRun context.
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


class _WRFRunNamelist:
    """
    Manage all namelist configurations of NWP models.
    """

    def __init__(self):
        """
        Manage all namelist configurations of NWP models.

        This class provides interfaces to read and write various namelist values of NWP model.
        Namelist values are stored in a dictionary with a unique ``namelist_id`` to avoid being messed up with other namelist.

        If you want to use a new ``namelist_id`` other than the defaults to store namelist,
        you can register a new ``namelist_id`` with :meth:`_WRFRunNamelist.register_custom_namelist_id`.
        """
        self._namelist_dict = {}
        self._namelist_id_list = ("param", "geog_static_data", "wps", "wrf", "wrfda")

    def register_custom_namelist_id(self, namelist_id: str) -> bool:
        """
        Register a unique ``namelist_id`` so you can read, update and write namelist with it later.

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
        Unregister a ``namelist_id``.
        If unregister successfully, all values of this namelist will be deleted.

        :param namelist_id: A unique namelist id.
        :type namelist_id: str
        """
        if namelist_id not in self._namelist_id_list:
            return

        self.delete_namelist(namelist_id)
        self._namelist_id_list = tuple(set(self._namelist_id_list) - {namelist_id, })

    def check_namelist_id(self, namelist_id: str) -> bool:
        """
        Check if a ``namelist_id`` is registered.

        :param namelist_id: A ``namelist_id``.
        :type namelist_id: str
        :return: True if the ``namelist_id`` is registered, else False.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list:
            return True
        else:
            return False

    def read_namelist(self, file_path: str, namelist_id: str):
        """
        Read namelist values from a file and store them with the ``namelist_id``.

        If ``wrfrun`` can't read the file, ``FileNotFoundError`` will be raised.
        If ``namelist_id`` isn't registered, :class:`NamelistIDError` will be raised.

        :param file_path: Namelist file path.
        :type file_path: str
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        # check the file path
        if not exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError

        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

        self._namelist_dict[namelist_id] = f90nml.read(file_path).todict()

    def write_namelist(self, save_path: str, namelist_id: str, overwrite=True):
        """
        Write namelist values of a ``namelist_id`` to a file.

        :param save_path: Target file path.
        :type save_path: str
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :param overwrite: If overwrite the existed file.
        :type overwrite: bool
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

        if namelist_id not in self._namelist_dict:
            logger.error(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
            raise NamelistError(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")

        f90nml.Namelist(self._namelist_dict[namelist_id]).write(save_path, force=overwrite)

    def update_namelist(self, new_values: Union[str, dict], namelist_id: str):
        """
        Update namelist values of a ``namelist_id``.

        You can give the path of a whole namelist file or a file only contains values you want to change.

        >>> namelist_file = "./namelist.wps"
        >>> WRFRUNConfig.update_namelist(namelist_file, namelist_id="wps")

        >>> namelist_file = "./namelist.wrf"
        >>> WRFRUNConfig.update_namelist(namelist_file, namelist_id="wrf")

        You can also give a dict contains values you want to change.

        >>> namelist_values = {"ungrib": {"prefix": "./output/FILE"}}
        >>> WRFRUNConfig.update_namelist(namelist_values, namelist_id="wps")

        >>> namelist_values = {"time_control": {"debug_level": 100}}
        >>> WRFRUNConfig.update_namelist(namelist_values, namelist_id="wrf")

        :param new_values: The path of a namelist file, or a dict contains namelist values.
        :type new_values: str | dict
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

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
        Get namelist values of a ``namelist_id``.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :return: A dictionary which contains namelist values.
        :rtype: dict
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")
        elif namelist_id not in self._namelist_dict:
            logger.error(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
            raise NamelistError(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
        else:
            return deepcopy(self._namelist_dict[namelist_id])

    def delete_namelist(self, namelist_id: str):
        """
        Delete namelist values of a ``namelist_id``.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")

        if namelist_id not in self._namelist_dict:
            return

        self._namelist_dict.pop(namelist_id)

    def check_namelist(self, namelist_id: str) -> bool:
        """
        Check if a namelist has been registered and loaded.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :return: ``True`` if it is registered and loaded, else ``False``.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list and self._namelist_dict:
            return True

        else:
            return False


class WRFRunConfig(_WRFRunConstants, _WRFRunNamelist, _WRFRunResources):
    """
    Class to manage wrfrun config, runtime constants, namelists and resource files.
    """
    _instance = None
    _initialized = False

    def __init__(self):
        """
        This class provides various interfaces to access ``wrfrun``'s config, namelist values of NWP models,
        runtime constants and resource files by inheriting from:
        :class:`_WRFRunConstants`, :class:`_WRFRunNamelist` and :class:`_WRFRunResources`.

        An instance of this class called ``WRFRUNConfig`` will be created after the user import ``wrfrun``,
        and you should use the instance to access configs or other things instead of creating another instance.
        """
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
        Set file path of the config template file.

        :param file_path: Template file path.
        :type file_path: str
        """
        self._config_template_file_path = file_path

    def load_wrfrun_config(self, config_path: Optional[str] = None):
        """
        Load ``wrfrun`` config from a config file.

        If the config path is invalid, ``wrfrun`` will create a new config file at the same place,
        and raise ``FileNotFoundError``.

        If you don't give the config path, ``wrfrun`` will create a new config file under the current directory,
        and read it.

        :param config_path: TOML config file. Defaults to None.
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

        config_dir_path = abspath(dirname(config_path))

        # merge model config.
        keys_list = list(self._config["model"].keys())
        for model_key in keys_list:

            # skip the key that isn't model.
            if model_key == "debug_level":
                continue

            if "use" not in self._config["model"][model_key]:
                continue

            if self._config["model"][model_key]["use"]:
                include_file = self._config["model"][model_key]["include"]
                if include_file[0] != "/":
                    include_file = f"{config_dir_path}/{include_file}"

                with open(include_file, "rb") as f:
                    self._config["model"][model_key] = tomli.load(f)

            else:
                self._config["model"].pop(model_key)

        # register URI for output directory.
        output_path = abspath(self["output_path"])
        self.register_resource_uri(self.WRFRUN_OUTPUT_PATH, output_path)

    def save_wrfrun_config(self, save_path: str):
        """
        Save ``wrfrun``'s config to a file.

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
        You can access ``wrfrun`` config like the way to access values in a dictionary.

        For example

        >>> model_config = WRFRUNConfig["model"]    # get all model configs.

        :param item: Keys.
        :type item: str
        """
        if len(self._config) == 0:
            logger.error("Attempt to read value before load config")
            raise RuntimeError("Attempt to read value before load config")

        return deepcopy(self._config[item])

    def get_input_data_path(self) -> str:
        """
        Get the path of directory in which stores the input data.

        :return: Directory path.
        :rtype: str
        """
        return deepcopy(self["input_data_path"])

    def get_model_config(self, model_name: str) -> dict:
        """
        Get the config of a NWP model.

        An exception :class:`ModelNameError` will be raised if the config can't be found.

        :param model_name: Name of the model. For example, ``wrf``.
        :type model_name: str
        :return: A dictionary.
        :rtype: dict
        """
        if model_name not in self["model"]:
            logger.error(f"Config of model '{model_name}' isn't found in your config file.")
            raise ModelNameError(f"Config of model '{model_name}' isn't found in your config file.")

        return deepcopy(self["model"][model_name])

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


WRFRUNConfig = WRFRunConfig()

__all__ = ["WRFRUNConfig"]
