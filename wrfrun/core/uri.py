"""
wrfrun.core.uri
###############

.. autosummary::
    :toctree: generated/

    WRFRUNURI

WRFRUNURI
*********

This class provides methods to access and manage internal URIs used by ``wrfrun``.

URIs in wrfrun
==============

``wrfrun`` uses URI (Uniform Resource Identifier) to represents real file / directory pathes,
to make sure the same code works on different machines.

There are some additional restrictions about URIs used in wrfrun:

* Must start with ``:WRFRUN_``
* Must end with ``:``

Register URIs
=============

There are two ways to register URI:

**Register directly**

The most convenient way to register resource uri is using :meth:`register_resource_uri <WRFRUNURI.register_resource_uri>`.

.. code-block:: Python
    :caption: main.py

    resource = WRFRUNURI(work_dir="./.wrfrun")
    resource_uri = ":WRFRUN_TEST_URI:"

    # remember to check if it has been registered.
    if not resource.check_resource_uri(resource_uri):
        resource.register_resource_uri(resource_uri)

**Use register function**

Please see documentation about :class:`WRFRUN <wrfrun.core.core._WRFRUNProxy>`.

Parse URIs
==========

You can get the real file path using :meth:`parse_resource_uri <WRFRUNURI.parse_resource_uri>`,
it will parse all the URIs in the string.

.. code-block:: Python
    :caption: main.py

    from wrfrun.core import WRFRUN
    workspace_path = f"{WRFRUN.uri.WRFRUN_WORKSPACE_ROOT}/WPS"    # ":WRFRUN_WORKSPACE_PATH:/WPS"
    # real_path should be a valid path like: "/home/syize/.config/wrfrun/workspace/WPS"
    real_path = WRFRUN.uri.parse_resource_uri(workspace_path)
"""

from os import environ
from os.path import abspath
from sys import platform

from ..log import logger
from .error import ResourceURIError


class WRFRUNURI:
    """
    Define all variables that will be used by other components.
    """

    def __init__(self, work_dir: str, *args, **kwargs):
        """
        Define all variables that will be used by other components.

        These variables are related to ``wrfrun`` installation environments, configuration files and more.
        They are defined either directly or mapped using URIs to ensure consistent access across all components.

        :param work_dir: ``wrfrun`` work directory path.
        :type work_dir: str
        """
        # check system
        if platform != "linux":
            logger.debug("Not Linux system!")

        if work_dir != "" or platform != "linux":
            # set temporary dir path
            self._WRFRUN_TEMP_PATH = abspath(f"{work_dir}/tmp")
            self._WRFRUN_HOME_PATH = abspath(work_dir)

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

        self._WRFRUN_OUTPUT_PATH = ":WRFRUN_OUTPUT_PATH:"
        self._WRFRUN_RESOURCE_PATH = ":WRFRUN_RESOURCE_PATH:"

        self._resource_namespace_db = {}

        super().__init__(*args, **kwargs)

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

    def check_resource_uri(self, unique_uri: str) -> bool:
        """
        Check if the URI has been registered.

        ``wrfrun`` uses unique URIs to represent file / directory path.
        If you want to register a URI, you need to check if it's available.

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
        Register a path with a URI.
        The URI should start with ``:WRFRUN_``, end with ``:`` and hasn't been registered yet,
        otherwise an exception :class:`ResourceURIError <wrfrun.core.error.ResourceURIError>` will be raised.

        :param unique_uri: Unique URI represents the resource.
                           It must start with ``:WRFRUN_`` and end with ``:``. For example, ``":WRFRUN_WORK_PATH:"``.
        :type unique_uri: str
        :param res_space_path: REAL absolute path of your resource path. For example, "$HOME/.config/wrfrun/res".
        :type res_space_path: str
        """
        if not (unique_uri.startswith(":WRFRUN_") and unique_uri.endswith(":")):
            logger.error(f"Can't register URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")
            raise ResourceURIError(f"Can't register URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")

        if unique_uri in self._resource_namespace_db:
            logger.error(f"URI '{unique_uri}' exists.")
            raise ResourceURIError(f"URI '{unique_uri}' exists.")

        logger.debug(f"Register URI '{unique_uri}' to '{res_space_path}'")
        self._resource_namespace_db[unique_uri] = res_space_path

    def unregister_resource_uri(self, unique_uri: str):
        """
        Unregister a URI.

        :param unique_uri: Registered URI.
        :type unique_uri: str
        """
        if unique_uri in self._resource_namespace_db:
            self._resource_namespace_db.pop(unique_uri)

    def parse_resource_uri(self, resource_path: str) -> str:
        """
        Return the converted string by parsing the URI string in it.
        Normal path will be returned with no change.

        If the URI hasn't been registered, an exception :class:`ResourceURIError` will be raised.

        For example, you can get the real path of ``wrfrun`` workspace with this method:

        >>> from wrfrun.core import WRFRUN
        >>> workspace_path = f"{WRFRUN.uri.WRFRUN_WORKSPACE_ROOT}/WPS"    # ":WRFRUN_WORKSPACE_ROOT:/WPS"
        >>> # real_path should be a valid path like: "/home/syize/.config/wrfrun/workspace/WPS"
        >>> real_path = WRFRUN.uri.parse_resource_uri(workspace_path)

        :param resource_path: Resource path string which may contain URI string.
        :type resource_path: str
        :return: Real resource path.
        :rtype: str
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


__all__ = ["WRFRUNURI"]
