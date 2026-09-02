"""
wrfrun.core.runtime.io
######################

This module handles file processes.

.. autosummary::
    :toctree: generated/

    IOService
"""

import logging
from os import remove, symlink
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

    def process(self, file_config: FileConfigDict, is_move=False, is_copy=False, overwrite=False):
        """
        Handle file processes, copy, move, or link the target to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        :param is_move: If move the file, defaults to False
        :type is_move: bool, optional
        :param is_copy: If copy the file, defaults to False
        :type is_copy: bool, optional
        :param overwrite: If overwrite exists file.
        :type overwrite: bool
        :raises FileNotFoundError: File doesn't exist.
        :raises FileNotFoundError: Input target exists, but isn't a file.
        :raises FileExistsError: Save target exists, but overwrite=False.
        """
        file_path = file_config["file_path"]
        save_path = file_config["save_path"]

        file_path = self._resource.get_resource(file_path)
        save_path = self._resource.get_custom_resource(save_path)

        LOGGER.debug(f"Parse file '{file_path}' to '{file_path}'")

        if not file_path.exists():
            message = f"'{file_path}' doesn't exist."
            LOGGER.error(message)
            raise FileNotFoundError(message)
        elif not file_path.is_file():
            message = f"'{file_path}' is not a file."
            LOGGER.error(message)
            raise FileNotFoundError(message)

        save_path.parent.mkdir(exist_ok=True)

        if save_path.is_file():
            if overwrite:
                LOGGER.warning(f"Target file '{save_path}' exists, overwrite it.")
                remove(save_path)

            else:
                message = f"Target file '{save_path}' exists, backup it or set overwrite=True."
                LOGGER.error(message)
                raise FileExistsError(message)

        if is_copy:
            copyfile(file_path, save_path)

        elif is_move:
            move(file_path, save_path)

        else:
            symlink(file_path, save_path)

    def copy(self, file_config: FileConfigDict, overwrite=False):
        """
        Copy file to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        :param overwrite: If overwrite exists file.
        :type overwrite: bool
        """
        self.process(file_config, is_copy=True, overwrite=overwrite)

    def move(self, file_config: FileConfigDict, overwrite=False):
        """
        Move file to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        :param overwrite: If overwrite exists file.
        :type overwrite: bool
        """
        self.process(file_config, is_move=True, overwrite=overwrite)

    def symlink(self, file_config: FileConfigDict, overwrite=False):
        """
        Link file to the destination.

        :param file_config: File config.
        :type file_config: FileConfigDict
        :param overwrite: If overwrite exists file.
        :type overwrite: bool
        """
        self.process(file_config, overwrite=overwrite)

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
