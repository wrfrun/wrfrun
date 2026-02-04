"""
wrfrun.core._resource
#####################

.. autosummary::
    :toctree: generated/

    ResourceMixIn

ResourceMixIn
*************

This class provides methods to manage resources in wrfrun.

URIs in wrfrun
==============

``wrfrun`` uses URI (Uniform Resource Identifier) to represents real resource files,
to make sure the same code works on different machines.

There are some additional restrictions about URIs used in wrfrun:

* Must start with ``:WRFRUN_``
* Must end with ``:``

Register URIs
=============

There are two ways to register URI:

**Register directly**

The most convenient way to register resource uri is using :meth:`register_resource_uri <ResourceMixIn.register_resource_uri>`.

.. code-block:: Python
    :caption: main.py

    resource = ResourceMixIn()
    resource_uri = ":WRFRUN_TEST_URI:"

    # remember to check if it has been registered.
    if not resource.check_resource_uri(resource_uri):
        resource.register_resource_uri(resource_uri)

**Use register function**

Please see documentation about :class:`WRFRUN <wrfrun.core.core._WRFRUNProxy>`.

Parse URIs
==========

You can get the real file path using :meth:`parse_resource_uri <ResourceMixIn.parse_resource_uri>`,
it will parse all the URIs in the string.
"""

from ..log import logger
from .error import ResourceURIError


class ResourceMixIn:
    """
    This class provides methods to manage resources in wrfrun.

    These resources may include various configuration files from NWP as well as those provided by wrfrun itself.
    Since their actual file paths may vary depending on the installation environment,
    wrfrun maps them using URIs to ensure consistent access regardless of the environment.

    The URI always starts with the prefix string ``:WRFRUN_`` and ends with ``:``.

    To register URIs, user can use :meth:`ResourceMixIn.register_resource_uri`.

    To convert any possible URIs in a string, user can use :meth:`ResourceMixIn.parse_resource_uri`.
    """

    def __init__(self, *args, **kwargs):
        self._resource_namespace_db = {}

        super().__init__(*args, **kwargs)

    def check_resource_uri(self, unique_uri: str) -> bool:
        """
        Check if the URI has been registered.

        ``wrfrun`` uses unique URIs to represent resource files.
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
        Register a resource path with a URI.
        The URI should start with ``:WRFRUN_`` ,end with ``:`` and hasn't been registered yet,
        otherwise an exception :class:`ResourceURIError <wrfrun.core.error.ResourceURIError>` will be raised.

        :param unique_uri: Unique URI represents the resource.
                           It must start with ``:WRFRUN_`` and end with ``:``. For example, ``":WRFRUN_WORK_PATH:"``.
        :type unique_uri: str
        :param res_space_path: REAL absolute path of your resource path. For example, "$HOME/.config/wrfrun/res".
        :type res_space_path: str
        """
        if not (unique_uri.startswith(":WRFRUN_") and unique_uri.endswith(":")):
            logger.error(f"Can't register resource URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'.")
            raise ResourceURIError(
                f"Can't register resource URI: '{unique_uri}'. It should start with ':WRFRUN_' and end with ':'."
            )

        if unique_uri in self._resource_namespace_db:
            logger.error(f"Resource URI '{unique_uri}' exists.")
            raise ResourceURIError(f"Resource URI '{unique_uri}' exists.")

        logger.debug(f"Register URI '{unique_uri}' to '{res_space_path}'")
        self._resource_namespace_db[unique_uri] = res_space_path

    def unregister_resource_uri(self, unique_uri: str):
        """
        Unregister a resource URI.

        :param unique_uri: Unique URI represents the resource.
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
        >>> workspace_path = f"{WRFRUN.config.WRFRUN_WORKSPACE_ROOT}/WPS"    # ":WRFRUN_WORKSPACE_PATH:/WPS"
        >>> # real_path should be a valid path like: "/home/syize/.config/wrfrun/workspace/WPS"
        >>> real_path = WRFRUN.config.parse_resource_uri(workspace_path)

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


__all__ = ["ResourceMixIn"]
