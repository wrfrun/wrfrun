"""
wrfrun.core.core
################

.. autosummary::
    :toctree: generated/

    WRFRUNProxy
    WRFRUN

Global variable "WRFRUN"
************************

``WRFRUN`` is an instance of :class:`WRFRUNProxy`.
It holds the instance of :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`,
:class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`,
and :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`.
Through this global variable, other submodules of wrfrun and users can access attributes and methods of these classes.
"""

from contextvars import ContextVar, Token
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from wrfrun.utils import check_path

from ..log import logger
from ._config import WRFRunConfig
from ._exec_db import ExecutableDB
from ._record import ExecutableRecorder
from .error import ConfigError, WRFRunContextError
from .runtime import ExecutableRegistry, IOService, RecordService, ResourceCatalog, RunnerService, RuntimeService
from .states import ConfigService, NamelistService, StatesService, WRFRunStates
from .uri import WRFRUNURI


@dataclass(frozen=True)
class WRFRunSession:
    runtime: RuntimeService

    states: StatesService


RUNTIME_SESSION: ContextVar[WRFRunSession | None] = ContextVar(
    "wrfrun_runtime_session",
    default=None,
)


class WRFRUNProxy:
    """
    Proxy class to access :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`,
    :class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`,
    :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`,
    and :class:`WRFRUNURI <wrfrun.core.uri.WRFRUNURI>`
    """

    def __init__(self):
        """
        Proxy class to access :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`,
        :class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`,
        :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`,
        and :class:`WRFRUNURI <wrfrun.core.uri.WRFRUNURI>`
        """
        self._config: WRFRunConfig | None = None
        self._config_initialized = False
        self._exec_db: ExecutableDB | None = None
        self._exec_db_initialized = False
        self._recorder: ExecutableRecorder | None = None
        self._recorder_initialized = False
        self._uri_manager: ResourceCatalog | None = None
        self._uri_manager_initialized = False

        self._io_service: IOService | None = None
        self._io_service_initialized = False

        self._config_register_funcs: list[Callable[["WRFRunConfig"], None]] = []
        self._uri_register_funcs: list[Callable[["WRFRUNURI"], None]] = []
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
    def uri(self) -> ResourceCatalog:
        """
        Access ResourceCatalog.

        :return: Resource manager.
        :rtype: ResourceCatalog
        """
        if self._uri_manager is None:
            logger.error("You haven't initialize `ResourceCatalog` yet.")
            raise ConfigError("You haven't initialize `ResourceCatalog` yet.")
        return self._uri_manager

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

    @property
    def io(self) -> IOService:
        """
        Access IO service.

        :raises ConfigError: IO service isn't initialized.
        :return: IO service.
        :rtype: IOService
        """
        if self._io_service is None:
            logger.error("You haven't initialize IO service yet.")
            raise ConfigError("You haven't initialize IO service yet.")

        return self._io_service

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
        This function should accept a ``WRFRunConfig`` instance.

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

    def set_uri_register_func(self, func: Callable[["WRFRUNURI"], None]):
        """
        Set register function which will be called by WRFRUNURI.
        This function should accept a ``WRFRUNURI`` instance.

        If WRFRUNURI hasn't been initialized, the function will be stored
        and called in order by the time WRFRUNURI is initialized.

        :param func: Register functions.
        :type func: Callable[["WRFRUNURI"], None]
        """
        logger.warning("This hook is deprecated. Please use new resource manager.")
        if self._uri_manager_initialized:
            func(self._uri_manager.old_uri)  # type: ignore

        else:
            if func not in self._uri_register_funcs:
                self._uri_register_funcs.append(func)

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

    def is_initialized(self, name: Literal["config", "exec_db", "record", "uri"]) -> bool:
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

            case "uri":
                flag = self._uri_manager_initialized

        return flag

    def init_wrfrun_config(self, config_file: str):
        """
        Initialize wrfrun config with the given config file.

        :param config_file: Config file path.
        :type config_file: str
        """
        logger.info(f"Read config: '{config_file}'")
        self._config = WRFRunConfig.from_config_file(self.uri.old_uri, config_file, self._config_register_funcs)
        self._config_initialized = True

        self.uri.register_provider("project", Path(config_file).resolve().parent)

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

    def init_uri_manager(self, work_dir: str):
        """
        Initialize URI manager.

        :param work_dir: wrfrun work directory path.
        :type work_dir: str
        """
        self._uri_manager = ResourceCatalog(work_dir)
        for _func in self._uri_register_funcs:
            _func(self._uri_manager.old_uri)

        self._io_service = IOService(self._uri_manager)

        self._uri_register_funcs = []
        self._uri_manager_initialized = True

        self._io_service_initialized = True

    def check_path(self, *args):
        """
        Helper function to check and create directories.

        This helper wraps the utility function :func:`check_path <wrfrun.utils.check_path>`,
        it will convert URIs to real path first.
        """
        real_path = (self.uri.parse_resource_uri(_path) for _path in args)
        check_path(*real_path)


# WRFRUN_NEW = WRFRUNProxy()


class WRFRunVarAPI:
    """
    Port to access ``wrfrun`` runtime services and states.
    """

    @property
    def session(self) -> WRFRunSession:
        """
        Access ``wrfrun`` runtime session, which stores runtime services and states.

        :raises WRFRunContextError: No active ``wrfrun`` session.
        :return: Active ``wrfrun`` session.
        :rtype: WRFRunSession
        """
        session = RUNTIME_SESSION.get()
        if session is None:
            raise WRFRunContextError("No active WRFRun session.")

        return session

    @property
    def io(self) -> IOService:
        """
        IO service.

        :return: IO service.
        :rtype: IOService
        """
        return self.session.runtime.io

    @property
    def record(self) -> RecordService:
        """
        Record service.

        :return: Record service.
        :rtype: RecordService
        """
        return self.session.runtime.record

    @property
    def resource(self) -> ResourceCatalog:
        """
        Resource manager.

        :return: Resource manager.
        :rtype: ResourceCatalog
        """
        return self.session.runtime.resource

    @property
    def registry(self) -> ExecutableRegistry:
        """
        ``Executable`` registry.

        :return: ``Executable`` registry.
        :rtype: ExecutableRegistry
        """
        return self.session.runtime.registry

    @property
    def runner(self) -> RunnerService:
        """
        External command runner service.

        :return: Runner service.
        :rtype: RunnerService
        """
        return self.session.runtime.runner

    @property
    def config(self) -> ConfigService:
        """
        ``wrfrun`` configs.

        :return: ``wrfrun`` configs.
        :rtype: ConfigService
        """
        return self.session.states.config

    @property
    def namelist(self) -> NamelistService:
        """
        Stored namelists.

        :return: Stored namelists.
        :rtype: NamelistService
        """
        return self.session.states.namelist

    @property
    def states(self) -> WRFRunStates:
        """
        ``wrfrun`` runtime states.

        :return: ``wrfrun`` runtime states.
        :rtype: WRFRunStates
        """
        return self.session.states.states

    def set_session(self, session: WRFRunSession) -> Token[WRFRunSession | None]:
        """
        Save new ``wrfrun`` session to the context.

        :param session: New ``wrfrun`` session.
        :type session: WRFRunSession
        :return: Session token.
        :rtype: Token[WRFRunSession | None]
        """
        return RUNTIME_SESSION.set(session)

    def reset_session(self, token: Token[WRFRunSession]):
        """
        Delete the session which belongs to the given token.

        :param token: Session token.
        :type token: Token[WRFRunSession]
        """
        return RUNTIME_SESSION.reset(token)


WRFRUN_NEW = WRFRunVarAPI()


def create_wrfrun_session(work_dir: str) -> Token[WRFRunSession | None]:
    """
    Helper function to create new wrfrun session.

    :param work_dir: Work directory path.
    :type work_dir: str
    :return: Session token
    :rtype: Token[WRFRunSession | None]
    """
    resource = ResourceCatalog(work_dir)
    io = IOService(resource)
    record = RecordService(resource)
    registry = ExecutableRegistry()
    runner = RunnerService(resource)

    config = ConfigService(io, resource)
    namelist = NamelistService(io)
    states = WRFRunStates()

    wrfrun_session = WRFRunSession(
        runtime=RuntimeService(
            io=io,
            record=record,
            registry=registry,
            resource=resource,
            runner=runner,
        ),
        states=StatesService(
            config=config,
            namelist=namelist,
            states=states,
        ),
    )

    return WRFRUN_NEW.set_session(wrfrun_session)


__all__ = ["WRFRUNProxy", "WRFRunVarAPI", "WRFRUN_NEW", "create_wrfrun_session"]
