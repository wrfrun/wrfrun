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

from ..type import FileConfigDict
from .resource import ResourceCatalog

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


__all__ = ["IOService"]
