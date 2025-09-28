"""
wrfrun.core.replay
##################

This module provides methods to read config from ``.replay`` file and reproduce the simulation.

.. autosummary::
    :toctree: generated/

    WRFRunExecutableRegisterCenter
    replay_config_generator

WRFRUNExecDB
************

In order to load ``Executable`` correctly based on the stored ``name`` in ``.replay`` files,
``wrfrun`` uses ``WRFRUNExecDB``, which is the instance of :class:`WRFRunExecutableRegisterCenter`,
to records all ``Executable`` classes and corresponding ``name``.
When ``wrfrun`` replays the simulation, it gets the right ``Executable`` from ``WRFRUNExecDB`` and executes it.
"""

from collections.abc import Generator
from json import loads
from os.path import exists
from shutil import unpack_archive
from typing import Any

from .base import ExecutableBase, ExecutableConfig
from .config import WRFRUNConfig
from .error import ExecRegisterError, GetExecClassError
from ..utils import logger

WRFRUN_REPLAY_URI = ":WRFRUN_REPLAY:"


class WRFRunExecutableRegisterCenter:
    """
    This class provides the method to records ``Executable``'s class with a unique ``name``.
    Later you can get the class with the ``name``.
    """
    _instance = None
    _initialized = False

    def __init__(self):
        if self._initialized:
            return

        self._exec_db = {}

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def register_exec(self, name: str, cls: type):
        """
        Register an ``Executable``'s class with a unique ``name``.

        If the ``name`` has been used, :class:`ExecRegisterError` will be raised.

        :param name: ``Executable``'s unique name.
        :type name: str
        :param cls: ``Executable``'s class.
        :type cls: type
        """
        if name in self._exec_db:
            logger.error(f"'{name}' has been registered.")
            raise ExecRegisterError(f"'{name}' has been registered.")

        self._exec_db[name] = cls

    def is_registered(self, name: str) -> bool:
        """
        Check if an ``Executable``'s class has been registered.

        :param name: ``Executable``'s unique name.
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
        Get an ``Executable``'s class with the ``name``.

        If the ``name`` can't be found, :class:`GetExecClassError` will be raised.

        :param name: ``Executable``'s unique name.
        :type name: str
        :return: ``Executable``'s class.
        :rtype: type
        """
        if name not in self._exec_db:
            logger.error(f"Executable class '{name}' not found.")
            raise GetExecClassError(f"Executable class '{name}' not found.")

        return self._exec_db[name]


WRFRUNExecDB = WRFRunExecutableRegisterCenter()


def replay_config_generator(replay_config_file: str) -> Generator[tuple[str, ExecutableBase], Any, None]:
    """
    This method can read the ``.replay`` file and returns a generator which yields ``Executable`` and their names.
    If this method doesn't find ``config.json`` in the ``.replay`` file, ``FileNotFoundError`` will be raised.

    The ``Executable`` you get from the generator has been initialized so you can execute it directly.

    >>> replay_file = "./example.replay"
    >>> for name, _exec in replay_config_generator(replay_file):
    >>>     _exec.replay()

    :param replay_config_file: Path of the ``.replay`` file.
    :type replay_config_file: str
    :return: A generator that yields: ``(name, Executable)``
    :rtype: Generator
    """
    logger.info(f"Loading replay resources from: {replay_config_file}")
    work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_WORKSPACE_REPLAY)

    unpack_archive(replay_config_file, work_path, "zip")

    if not exists(f"{work_path}/config.json"):
        logger.error("Can't find replay config in the provided config file.")
        raise FileNotFoundError("Can't find replay config in the provided config file.")

    with open(f"{work_path}/config.json", "r") as f:
        replay_config_list: list[ExecutableConfig] = loads(f.read())

    for _config in replay_config_list:
        args = _config["class_config"]["class_args"]
        kwargs = _config["class_config"]["class_kwargs"]
        executable: ExecutableBase = WRFRUNExecDB.get_cls(_config["name"])(*args, **kwargs)
        executable.load_config(_config)
        yield _config["name"], executable


__all__ = ["WRFRUNExecDB", "replay_config_generator"]
