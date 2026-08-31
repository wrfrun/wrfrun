"""
wrfrun.core.runtime.registry
############################

Registry service is used to manage ``Executable`` information.
``wrfrun`` will load ``Executable`` which is needed by the simulation after loading config file, record them,
and provide them to replay service.

.. autosummary::
    :toctree: generated/

    ExecutableRegistry
"""

import logging

from ..error import ExecRegisterError, GetExecClassError

LOGGER = logging.getLogger("wrfrun")


class ExecutableRegistry:
    """
    Service to manage ``Executable`` information.
    """

    def __init__(self):
        """
        Service to manage ``Executable`` information.
        """
        self._exec_db = {}

    def register_exec(self, name: str, cls: type):
        """
        Register an ``Executable`` with a unique ``name``.

        If the ``name`` has been used, :class:`ExecRegisterError <wrfrun.core.error.ExecRegisterError>` will be raised.

        :param name: Unique name.
        :type name: str
        :param cls: ``Executable`` class.
        :type cls: type
        """
        if name in self._exec_db:
            LOGGER.error(f"'{name}' has been registered.")
            raise ExecRegisterError(f"'{name}' has been registered.")

        self._exec_db[name] = cls

    def unregister_exec(self, name: str):
        """
        Unregister an ``Executable``.

        :param name: Unique name.
        :type name: str
        """
        if name in self._exec_db:
            LOGGER.debug(f"Unregister Executable: '{name}'.")
            self._exec_db.pop(name)

    def is_registered(self, name: str) -> bool:
        """
        Check if an ``Executable`` has been registered.

        :param name: Unique name.
        :type name: str
        :return: True or False.
        :rtype: bool
        """
        if name in self._exec_db:
            return True
        else:
            return False

    def get_cls(self, name: str) -> type:
        """
        Get an ``Executable`` class with the ``name``.

        If the ``name`` can't be found, :class:`ExecRegisterError <wrfrun.core.error.ExecRegisterError>` will be raised.

        :param name: Unique name.
        :type name: str
        :return: ``Executable`` class.
        :rtype: type
        """
        if name not in self._exec_db:
            LOGGER.error(f"Executable class '{name}' not found.")
            raise GetExecClassError(f"Executable class '{name}' not found.")

        return self._exec_db[name]


__all__ = ["ExecutableRegistry"]
