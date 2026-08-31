"""
wrfrun.core.runtime.io
######################

This module handles file processes.

.. autosummary::
    :toctree: generated/

    IOService
"""

import logging
from os import symlink
from pathlib import Path
from shutil import copyfile, move

import f90nml
import tomli_w

from ..type import FileConfigDict
from .resource import ResourceCatalog, ResourceRef

LOGGER = logging.getLogger("wrfrun")


class IOService:
    """
    Handle file processes.
    """

    def __init__(self, resource: ResourceCatalog) -> None:
        """
        Handle file processes.

        :param resource: Resource manager.
        :type resource: ResourceCatalog
        """
        self._resource = resource

    def process(self, file_config: FileConfigDict, is_move=False, is_copy=False):
        """
        Handle file processes, copy, move, or link the target to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        :param is_move: If move the file, defaults to False
        :type is_move: bool, optional
        :param is_copy: If copy the file, defaults to False
        :type is_copy: bool, optional
        :raises FileNotFoundError: File doesn't exist.
        :raises FileNotFoundError: Target exists, but isn't a file.
        """
        file_path = file_config["file_path"]
        save_path = file_config["save_path"]
        save_name = file_config["save_name"]

        file_path = self._resource.parse_resource_uri(file_path)
        save_path = self._resource.parse_resource_uri(save_path)

        file_path = Path(file_path)
        save_path = Path(save_path) / save_name

        if not file_path.exists():
            message = f"'{file_path}' doesn't exist."
            LOGGER.error(message)
            raise FileNotFoundError(message)
        elif not file_path.is_file():
            message = f"'{file_path}' is not a file."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        save_path.parent.mkdir(exist_ok=True)

        if is_copy:
            copyfile(file_path, save_path)

        elif is_move:
            move(file_path, save_path)

        else:
            symlink(file_path, save_path)

    def copy(self, file_config: FileConfigDict):
        """
        Copy file to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        """
        self.process(file_config, is_copy=True)

    def move(self, file_config: FileConfigDict):
        """
        Move file to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        """
        self.process(file_config, is_move=True)

    def symlink(self, file_config: FileConfigDict):
        """
        Link file to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        """
        self.process(file_config)

    def write_namelist(self, content: dict, file_path: str | ResourceRef):
        """
        Write namelist to file.

        :param content: Namelist contents.
        :type content: dict
        :param file_path: File path, can be resource ref object or string.
        :type file_path: str | ResourceRef
        """
        if isinstance(file_path, ResourceRef):
            _save_path = self._resource.get_custom_resource(file_path)
        else:
            _save_path = Path(file_path)

        _save_path.parent.mkdir(exist_ok=True, parents=True)

        with open(_save_path, "w") as f:
            f90nml.write(content, f, force=True)

    def write_toml(self, content: dict, file_path: str | ResourceRef):
        """
        Write toml config.

        :param content: Contents.
        :type content: dict
        :param file_path: File path, can be resource ref object or string.
        :type file_path: str | ResourceRef
        """
        if isinstance(file_path, ResourceRef):
            _save_path = self._resource.get_custom_resource(file_path)
        else:
            _save_path = Path(file_path)

        _save_path.parent.mkdir(exist_ok=True, parents=True)

        with open(_save_path, "wb") as f:
            tomli_w.dump(content, f)


__all__ = ["IOService"]
