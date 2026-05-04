"""
wrfrun.worksapce.utils
######################

Utility functions for workspace creation.

.. autosummary::
    :toctree: generated/

    create_copy
"""

from os import remove, symlink
from os.path import exists
from shutil import copyfile
from typing import Literal

from wrfrun.log import logger


def create_copy(src_path: str, dst_path: str, mode: Literal["symlink", "copy"] = "symlink"):
    """
    Create a copy of ``src_path`` to ``dst_path``.

    :param src_path: Src file path.
    :type src_path: str
    :param dst_path: Destination file path.
    :type dst_path: str
    :param mode: Create mode, ``"symlink"`` or ``"copy"``, defaults to "symlink"
    :type mode: Literal["symlink", "copy"], optional
    :raises FileNotFoundError: Src file not found.
    :raises ValueError: ``mode`` is a wrong value.
    """
    if not exists(src_path):
        logger.error(f"File '{src_path}' doesn't exist.")
        raise FileNotFoundError(f"File '{src_path}' doesn't exist.")

    if exists(dst_path):
        logger.warning("Destination file exists, remove it and create new copy.")
        remove(dst_path)

    match mode:
        case "symlink":
            symlink(src_path, dst_path)

        case "copy":
            copyfile(src_path, dst_path)

        case _:
            logger.error(f"Unknown copy mode: '{mode}'")
            raise ValueError(f"Unknown copy mode: '{mode}'")


__all__ = ["create_copy"]
