"""
wrfrun.core._exec_db
####################

.. autosummary::
    :toctree: generated/

    ExecutableDB

ExecutableDB
************

To be able to replay simulations, ``wrfrun`` use this class to store ``Executable`` information.
When replaying simulations, ``wrfrun`` gets the corresponding ``Executable`` and calls it with its name.
"""

from typing import Callable

from ..log import logger
from .error import ExecRegisterError, GetExecClassError


class ExecutableDB:
    """
    This class provides the method to records ``Executable`` class with a unique ``name``.
    Later you can get the class with the ``name``.
    """

    def __init__(self):
        self._exec_db = {}

    def apply_register_func(self, func_list: list[Callable[["ExecutableDB"], None]]):
        """
        Call register function provided by other submodules.

        This method allows other submodules register ``Executable`` even after the whole wrfrun has been initialized.

        :param func_list: A list contains register functions.
        :type func_list: list[Callable[["WRFRunExecutableRegisterCenter"], None]]
        """
        while len(func_list) != 0:
            _func = func_list.pop(0)
            _func(self)

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
            logger.error(f"'{name}' has been registered.")
            raise ExecRegisterError(f"'{name}' has been registered.")

        self._exec_db[name] = cls

    def unregister_exec(self, name: str):
        """
        Unregister an ``Executable``.

        :param name: Unique name.
        :type name: str
        """
        if name in self._exec_db:
            logger.debug(f"Unregister Executable: '{name}'.")
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
            logger.error(f"Executable class '{name}' not found.")
            raise GetExecClassError(f"Executable class '{name}' not found.")

        return self._exec_db[name]


__all__ = ["ExecutableDB"]
