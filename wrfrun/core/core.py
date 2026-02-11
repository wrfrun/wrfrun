"""
wrfrun.core.core
################

.. autosummary::
    :toctree: generated/

    WRFRUNProxy

Global variable "WRFRUN"
************************

``WRFRUN`` is an instance of :class:`WRFRUNProxy`.
It holds the instance of :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`,
:class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`,
and :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`.
Through this global variable, other submodules of wrfrun and users can access attributes and methods of these classes.
"""

from typing import Callable, Literal

from ..log import logger
from ._config import WRFRunConfig
from ._exec_db import ExecutableDB
from ._record import ExecutableRecorder
from .error import ConfigError


class WRFRUNProxy:
    """
    Proxy class to access :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`,
    :class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`,
    and :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`.
    """

    def __init__(self):
        """
        Proxy class to access :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`,
        :class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`,
        and :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`.
        """
        self._config: WRFRunConfig | None = None
        self._config_initialized = False
        self._exec_db: ExecutableDB | None = None
        self._exec_db_initialized = False
        self._recorder: ExecutableRecorder | None = None
        self._recorder_initialized = False

        self._config_register_funcs: list[Callable[["WRFRunConfig"], None]] = []
        self._exec_db_register_funcs: list[Callable[["ExecutableDB"], None]] = []

        self.init_exec_db()

    @property
    def config(self) -> WRFRunConfig:
        """
        Access wrfrun config.

        :return: wrfrun config.
        :rtype: WRFRunConfig
        """
        if self._config is None:
            logger.error("You haven't initialize `CONFIG` yet.")
            raise ConfigError("You haven't initialize `CONFIG` yet.")
        return self._config

    @property
    def ExecDB(self) -> ExecutableDB:
        """
        Access Executable DB.

        :return: Executable DB.
        :rtype: ExecutableDB
        """
        if self._exec_db is None:
            logger.error("You haven't initialize `ExecDB` yet.")
            raise ConfigError("You haven't initialize `ExecDB` yet.")
        return self._exec_db

    @property
    def record(self) -> ExecutableRecorder:
        """
        Access simulation recorder.

        :return: Simulation recorder.
        :rtype: ExecutableRecorder
        """
        if self._recorder is None:
            logger.error("You haven't initialize simulation recorder yet.")
            raise ConfigError("You haven't initialize simulation recorder yet.")
        return self._recorder

    def set_exec_db(self, exec_db: ExecutableDB):
        """
        Initialize Executable DB.

        :param exec_db: Executables DB.
        :type exec_db: ExecutableDB
        """
        self._exec_db = exec_db
        self._exec_db_initialized = True

    def set_config_register_func(self, func: Callable[["WRFRunConfig"], None]):
        """
        Set register function which will be called by wrfrun config.
        This functions should accept a ``WRFRunConfig`` instance.

        If wrfrun config hasn't been initialized, the function will be stored
        and called in order by the time wrfrun config is initialized.

        :param func: Register functions.
        :type func: Callable[["WRFRunConfig"], None]
        """
        if self._config_initialized:
            func(self._config)

        else:
            if func not in self._config_register_funcs:
                self._config_register_funcs.append(func)

    def set_exec_db_register_func(self, func: Callable[["ExecutableDB"], None]):
        """
        Set register function which will be called by executables DB.
        This function should accept a :class:`WRFRunExecutableRegisterCenter` instance.

        If executables DB hasn't been initialized, the function will be stored
        and called in order by the time executables DB is initialized.

        :param func: Register functions.
        :type func: Callable[["WRFRunExecutableRegisterCenter"], None]
        """
        if self._exec_db_initialized:
            func(self._exec_db)

        else:
            if func not in self._exec_db_register_funcs:
                self._exec_db_register_funcs.append(func)

    def is_initialized(self, name: Literal["config", "exec_db", "record"]) -> bool:
        """
        Check if the config has been initialized.

        :param name: Name of the instance.
        :type name: str
        :return: True or False.
        :rtype: bool
        """
        flag = False

        match name:
            case "config":
                flag = self._config_initialized

            case "exec_db":
                flag = self._exec_db_initialized

            case "record":
                flag = self._recorder_initialized

        return flag

    def init_wrfrun_config(self, config_file: str):
        """
        Initialize wrfrun config with the given config file.

        :param config_file: Config file path.
        :type config_file: str
        """
        logger.info(f"Read config: '{config_file}'")
        self._config = WRFRunConfig.from_config_file(config_file, self._config_register_funcs)
        self._config_initialized = True

    def init_exec_db(self):
        """
        Initialize Executable DB.
        """
        self._exec_db = ExecutableDB()
        self._exec_db.apply_register_func(self._exec_db_register_funcs)
        self._exec_db_initialized = True

    def init_recorder(self, save_path: str, include_data: bool):
        """
        Initialize simulation recorder.

        :param save_path: Save path of the replay file.
        :type save_path: str
        :param include_data: If includes data.
        :type include_data: bool
        """
        self._recorder = ExecutableRecorder(self._config, save_path, include_data)
        self._recorder_initialized = True


WRFRUN = WRFRUNProxy()

__all__ = ["WRFRUN", "WRFRUNProxy"]
