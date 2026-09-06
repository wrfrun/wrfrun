"""
wrfrun.core.runtime.resource
############################

Component which provides access to wrfrun and project resources.

.. autosummary::
    :toctree: generated/

    ResourceType
    ResourceRef
    ResourceCatalog
"""

import logging
from importlib import resources
from pathlib import Path, PurePath

from ..type import ResourceRef, ResourceType
from ..uri import WRFRUNURI

LOGGER = logging.getLogger("wrfrun")


class ResourceCatalog:
    """
    This is wrfrun's resource manager.

    Register provider to it, then it can parse :class:`ResourceRef`, and give you the corresponding target file.

    By doing this, it is possible to represent file with the same url, even its real path can change on different machine.
    """

    def __init__(self, work_dir: str) -> None:
        """
        This is wrfrun's resource manager.

        Register provider to it, then it can parse :class:`ResourceRef`, and give you the corresponding target file.

        By doing this, it is possible to represent file with the same url, even its real path can change on different machine.
        """
        self._packages: dict[str, str] = {}
        self._work_path = Path(".wrfrun").resolve()
        self._old_uri = WRFRUNURI(work_dir)

        self.register_provider("core", "wrfrun.res")

        # runtime resource ref obj
        self._output = ResourceRef("project", "outputs")

    def register_provider(self, provider_name: str, provider_path: str | Path | ResourceRef) -> None:
        """
        Register a provider.

        The ``provider_name`` must be unique.

        The ``provider_path`` can be a package path (like ``wrfrun.res``), or a real path.

        **Example**

        1. Register wrfrun built-in res component:

        >>> resource = ResourceCatalog()
        >>> resource.register_provider("core", "wrfrun.res")

        2. Register custom provider:

        >>> resource = ResourceCatalog()
        >>> resource.register_provider("my_res_data", "data/res")

        :param provider_name: Provider name.
        :type provider_name: str | ResourceRef
        :param provider_path: Provider path (can be a package path, or real path)
        :type provider_path: str
        :raises ValueError: Provider already is registered.
        """
        if provider_name in self._packages:
            raise ValueError(f"Resource provider already registered: {provider_name}")

        if isinstance(provider_path, ResourceRef):
            _provider_path = self.get_custom_resource(provider_path)
        else:
            _provider_path = Path(provider_path).resolve()

        self._packages[provider_name] = _provider_path.as_posix()

    def unregister_provider(self, provider_name: str):
        """
        Unregister a provider.

        :param provider_name: Provider name.
        :type provider_name: str
        """
        if provider_name in self._packages:
            self._packages.pop(provider_name)

    def get_resource(self, ref: ResourceRef, resource_type=ResourceType.BOTH, check=True) -> Path:
        """
        Get resource with the given ref object.

        This method will check if the target exists if ``check = True``.

        :param ref: :class:`ResourceRef` object.
        :type ref: ResourceRef
        :param resource_type: Resource types, use enum class :class:`ResourceType`.
        :type resource_type: ResourceType | Literal[0, 1, 2]
        :param check: If ``True``, check if target exists.
        :type check: bool
        :raises KeyError: Provider of the ``ref`` isn't registered.
        :raises FileNotFoundError: ``ref`` is parsed successfully, but the target file isn't found.
        :return: Target file parsed from ``ref``.
        :rtype: Path
        """
        provider_path = self._packages.get(ref.provider, None)

        if provider_path is None:
            message = f"Unknown resource provider: {ref.provider}"
            LOGGER.error(message)
            raise KeyError(message)

        match resource_type:
            case ResourceType.PACKAGE:
                LOGGER.debug(f"Parse package resource: {ref.to_string()}.")
                resource = resources.files(provider_path).joinpath(*PurePath(ref.resource_path).parts)

            case ResourceType.REAL_FILE:
                LOGGER.debug(f"Parse normal resource: {ref.to_string()}.")
                resource = Path(provider_path) / ref.resource_path

            case ResourceType.BOTH:
                try:
                    resource = resources.files(provider_path).joinpath(*PurePath(ref.resource_path).parts)
                    LOGGER.debug(f"{ref.to_string()} is recognized as a package resource.")

                except ModuleNotFoundError:
                    resource = Path(provider_path) / ref.resource_path
                    LOGGER.debug(f"{ref.to_string()} is recognized as a normal resource.")

        if check and not resource.is_file():
            message = ""
            raise FileNotFoundError(str(resource))

        return resource.expanduser().resolve()  # type: ignore

    def get_package_resource(self, ref: ResourceRef, check=True) -> Path:
        """
        Get resource from Python package.

        :param ref: :class:`ResourceRef` object.
        :type ref: ResourceRef
        :param check: If ``True``, check if target exists, defaults to True.
        :type check: bool
        :return: Target file parsed from ``ref``.
        :rtype: Path
        """
        return self.get_resource(ref, ResourceType.PACKAGE, check)

    def get_custom_resource(self, ref: ResourceRef, check=False) -> Path:
        """
        Get custom resource.

        Parent directory will be created if you set ``auto_mkdir=True`` in resource ref.

        :param ref: :class:`ResourceRef` object.
        :type ref: ResourceRef
        :param check: If ``True``, check if target exists, defaults to False.
        :type check: bool
        :return: Target file parsed from ``ref``.
        :rtype: Path
        """
        resource = self.get_resource(ref, ResourceType.REAL_FILE, check)

        if ref.auto_mkdir:
            resource.parent.mkdir(exist_ok=True, parents=True)

        return resource

    def mkdir(self, ref: ResourceRef):
        """
        Create driectory of the resource.

        **NOTE**

        This method treats the entire resource path as a diirectory.

        :param ref: Resource ref object.
        :type ref: ResourceRef
        """
        self.get_custom_resource(ref).mkdir(parents=True, exist_ok=True)

    @property
    def CORE_RESOURCE(self):
        """
        ``wrfrun`` core resource root dir.

        :return: ResourceRef obj of ``wrfrun`` core resource root directory.
        :rtype: ResourceRef
        """
        return ResourceRef("core", "")

    @property
    def OUTPUT_DIR(self):
        """
        ``wrfrun`` output root directory.

        :return: ResourceRef obj of ``wrfrun`` output directory.
        :rtype: ResourceRef
        """
        return ResourceRef("output", "")

    @property
    def INPUT_DIR(self):
        """
        ``wrfrun`` input root directory.

        This is the directory to store input data.

        :return: ResourceRef obj of ``wrfrun`` input directory.
        :rtype: ResourceRef
        """
        return ResourceRef("input", "")

    @property
    def REPLAY_DIR(self):
        """
        ``wrfrun`` replay work directory.

        :return: ResourceRef obj of ``wrfrun`` input directory.
        :rtype: ResourceRef
        """
        return ResourceRef("replay", "")

    # ########################## Compatibility interface ###############################

    @property
    def old_uri(self) -> WRFRUNURI:
        """
        Compitability interface.

        :return: Old URI manager.
        :rtype: WRFRUNURI
        """
        return self._old_uri

    @property
    def WRFRUN_WORKSPACE_REPLAY(self) -> ResourceRef:
        """
        Path (URI) to store related files of ``wrfrun`` replay functionality.

        :return: URI.
        :rtype: str
        """
        return ResourceRef("workspace", "replay")

    @property
    def WRFRUN_TEMP_PATH(self) -> ResourceRef:
        """
        Path to store ``wrfrun`` temporary files.

        :return: URI
        :rtype: str
        """
        return ResourceRef("workspace", "temp")

    @property
    def WRFRUN_WORKSPACE_ROOT(self) -> ResourceRef:
        """
        Path of the root workspace.

        :return: URI
        :rtype: str
        """
        return ResourceRef("workspace", "")

    @property
    def WRFRUN_WORKSPACE_MODEL(self) -> ResourceRef:
        """
        Path of the model workspace, in which ``wrfrun`` runs numerical models.

        :return: URI
        :rtype: str
        """
        return ResourceRef("workspace", "model")

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
        return self._old_uri.check_resource_uri(unique_uri)

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
        return self._old_uri.register_resource_uri(unique_uri, res_space_path)

    def unregister_resource_uri(self, unique_uri: str):
        """
        Unregister a URI.

        :param unique_uri: Registered URI.
        :type unique_uri: str
        """
        return self._old_uri.unregister_resource_uri(unique_uri)

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
        return self._old_uri.parse_resource_uri(resource_path)


__all__ = ["ResourceType", "ResourceRef", "ResourceCatalog"]
