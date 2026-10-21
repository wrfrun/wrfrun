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

LOGGER = logging.getLogger("wrfrun")


PROJECT_TREE = (
    "configs/experiments",
    "configs/namelists/templates",
    "configs/namelists/user",
    "data/inputs/common",
    "data/inputs/experiments",
    "data/outputs",
    "logs",
)


class ResourceCatalog:
    """
    This is wrfrun's resource manager.

    Register provider to it, then it can parse :class:`ResourceRef`, and give you the corresponding target file.

    By doing this, it is possible to represent file with the same url, even its real path can change on different machine.
    """

    def __init__(self) -> None:
        """
        This is wrfrun's resource manager.

        Register provider to it, then it can parse :class:`ResourceRef`, and give you the corresponding target file.

        By doing this, it is possible to represent file with the same url, even its real path can change on different machine.
        """
        self._packages: dict[str, str] = {}
        self._work_path = Path(".wrfrun").resolve()

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
            _provider_path = self.get_custom_resource(provider_path).as_posix()
        else:
            _provider_path = provider_path

        self._packages[provider_name] = _provider_path

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

        # Avoid error from importlib
        provider_path = str(provider_path)

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

        LOGGER.debug(f"'{ref.to_string()}' is parsed to '{resource}'")

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

    def register_default_providers(self, project_path: str | Path, work_dir: str | Path):
        """
        Register default providers.

        :param project_path: Project root path.
        :type project_path: str
        :param work_dir: Work directory of ``wrfrun``.
        :type work_dir: str
        """
        _project_path = Path(project_path)
        _work_dir = Path(work_dir)
        self.register_provider("data", _project_path / "data")
        self.register_provider("project", _project_path)
        self.register_provider("config", _project_path / "configs")
        self.register_provider("workspace", _work_dir / "workspace")
        self.register_provider("temp", _work_dir / "temp")
        self.register_provider("replay", _work_dir / "replay")
        self.register_provider("log", _project_path / "logs")

    @property
    def CORE_RESOURCE(self):
        """
        ``wrfrun`` core resource root dir.

        :return: ResourceRef obj of ``wrfrun`` core resource root directory.
        :rtype: ResourceRef
        """
        return ResourceRef("core", "")

    @property
    def DATA_DIR(self):
        """
        ``wrfrun`` data dir.

        :return: ResourceRef obj of ``wrfrun`` data directory.
        :rtype: ResourceRef
        """
        return ResourceRef("data", "")

    @property
    def OUTPUT_DIR(self):
        """
        ``wrfrun`` output root directory.

        :return: ResourceRef obj of ``wrfrun`` output directory.
        :rtype: ResourceRef
        """
        return self.DATA_DIR / "outputs"

    @property
    def INPUT_DIR(self):
        """
        ``wrfrun`` input root directory.

        This is the directory to store input data.

        :return: ResourceRef obj of ``wrfrun`` input directory.
        :rtype: ResourceRef
        """
        return self.DATA_DIR / "inputs"

    @property
    def CONFIG_DIR(self) -> ResourceRef:
        """
        ``wrfrun`` config directory.

        :return: ResourceRef obj of ``wrfrun`` config directory.
        :rtype: ResourceRef
        """
        return ResourceRef("config", "")

    @property
    def NAMELIST_USER_DIR(self) -> ResourceRef:
        """
        ``wrfrun`` user namelist directory.

        :return: ResourceRef obj of ``wrfrun`` user namelist directory.
        :rtype: ResourceRef
        """
        return self.CONFIG_DIR / "namelists/user"

    @property
    def NAMELIST_TEMPLATE_DIR(self) -> ResourceRef:
        """
        ``wrfrun`` template namelist directory.

        :return: ResourceRef obj of ``wrfrun`` template namelist directory.
        :rtype: ResourceRef
        """
        return self.CONFIG_DIR / "namelists/templates"

    @property
    def WORKSPACE_DIR(self) -> ResourceRef:
        """
        Path of the root workspace.

        :return: URI
        :rtype: str
        """
        return ResourceRef("workspace", "")

    @property
    def REPLAY_DIR(self):
        """
        ``wrfrun`` replay work directory.

        :return: ResourceRef obj of ``wrfrun`` input directory.
        :rtype: ResourceRef
        """
        return ResourceRef("replay", "")

    @property
    def TEMP_DIR(self) -> ResourceRef:
        """
        Path to store ``wrfrun`` temporary files.

        :return: URI
        :rtype: str
        """
        return ResourceRef("temp", "")

    @property
    def LOG_DIR(self) -> ResourceRef:
        """
        Path to store ``wrfrun`` log files.

        :return: URI
        :rtype: str
        """
        return ResourceRef("log", "")


__all__ = ["ResourceType", "ResourceRef", "ResourceCatalog", "PROJECT_TREE"]
