"""
wrfrun.core._debug
##################

.. autosummary::
    :toctree: generated/

    DebugMixIn

DebugMixIn
**********

This class provides methods and attributes to debug ``wrfrun`` itself.

Attribute
=========

``DebugMixIn`` provides three attributes to set debug mode for different part.

* ``DEBUG_MODE``: ``bool`` attribute, basic switch for all other options. Defaults to ``False``.
* ``DEBUG_MODE_LOGGER``: ``bool | None`` attribute, switch for logging logger. If ``None``, use ``DEBUG_MODE`` value. Defaults to ``False``.
* ``DEBUG_MODE_EXECUTABLE``: ``bool | None`` attribute, switch for ``Executable``. If ``None``, use ``DEBUG_MODE`` value. Defaults to ``False``.

Environmental parameters
========================

``DebugMixIn`` also can read environmental variables.

* ``WRFRUN_DEBUG_MODE``: For ``DEBUG_MODE``, ``1`` or ``0``.
* ``WRFRUN_DEBUG_MODE_LOGGER``: For ``DEBUG_MODE_LOGGER``, ``1`` or ``0``.
* ``WRFRUN_DEBUG_MODE_EXECUTABLE``: For ``DEBUG_MODE_EXECUTABLE``, ``1`` or ``0``.
"""

import logging
from os import environ

from wrfrun.log import logger


class DebugMixIn:
    """
    Provide methods and attributes to debug ``wrfrun`` itself.
    """

    _environ_params = [
        "WRFRUN_DEBUG_MODE",
        "WRFRUN_DEBUG_MODE_LOGGER",
        "WRFRUN_DEBUG_MODE_EXECUTABLE",
    ]

    def __init__(self):
        """
        Provide methods and attributes to debug ``wrfrun`` itself.
        """
        self._debug_mode: bool = False
        self._debug_mode_logger: bool | None = None
        self._debug_mode_executable: bool | None = None

        if "WRFRUN_DEBUG_MODE" in environ:
            if environ["WRFRUN_DEBUG_MODE"]:
                self._debug_mode = True

            else:
                self._debug_mode = False

        if "WRFRUN_DEBUG_MODE_LOGGER" in environ:
            if environ["WRFRUN_DEBUG_MODE_LOGGER"]:
                self._debug_mode_logger = True

            else:
                self._debug_mode_logger = False

        if "WRFRUN_DEBUG_MODE_EXECUTABLE" in environ:
            if environ["WRFRUN_DEBUG_MODE_EXECUTABLE"]:
                self._debug_mode_executable = True

            else:
                self._debug_mode_executable = False

        self._change_log_level()

        super().__init__()

    @property
    def DEBUG_MODE(self) -> bool:
        """
        Base switch for all debug options.

        :return: If in debug mode.
        :rtype: bool
        """
        return self._debug_mode

    @DEBUG_MODE.setter
    def DEBUG_MODE(self, value: bool):
        self._debug_mode = value

    @property
    def DEBUG_MODE_LOGGER(self) -> bool:
        """
        Debug switch for logger.

        :return: If is in debug mode.
        :rtype: bool
        """
        if self._debug_mode_logger is None:
            return self._debug_mode
        else:
            return self._debug_mode_logger

    @DEBUG_MODE_LOGGER.setter
    def DEBUG_MODE_LOGGER(self, value: bool | None):
        self._debug_mode_logger = value
        self._change_log_level()

    @property
    def DEBUG_MODE_EXECUTABLE(self) -> bool:
        """
        Debug switch for ``Executable``.

        :return: If is in debug mode.
        :rtype: bool
        """
        if self._debug_mode_executable is None:
            return self._debug_mode
        else:
            return self._debug_mode_executable

    @DEBUG_MODE_EXECUTABLE.setter
    def DEBUG_MODE_EXECUTABLE(self, value: bool):
        self._debug_mode_executable = value

    def _change_log_level(self):
        """
        Change logging level when ``DEBUG_MODE_LOGGER`` is changed.
        """
        if self._debug_mode_logger is None and self._debug_mode:
            is_debug = True

        elif self._debug_mode_logger:
            is_debug = True

        else:
            is_debug = False

        if is_debug:
            logger.setLevel(logging.DEBUG)
            logger.info("Logger debug mode is on.")

        else:
            logger.setLevel(logging.INFO)
            logger.info("Logger debug mode is off.")


__all__ = ["DebugMixIn"]
