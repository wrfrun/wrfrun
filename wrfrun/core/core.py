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

from .error import WRFRunContextError
from .runtime import ExecutableRegistry, IOService, ReplayService, ResourceCatalog, RunnerService, RuntimeService
from .runtime.workspace import WorkspaceService
from .states import ConfigService, NamelistService, StatesService, WRFRunStates


@dataclass(frozen=True)
class WRFRunSession:
    runtime: RuntimeService

    states: StatesService


RUNTIME_SESSION: ContextVar[WRFRunSession | None] = ContextVar(
    "wrfrun_runtime_session",
    default=None,
)


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
    def replay(self) -> ReplayService:
        """
        Record and replay service.

        :return: Record service.
        :rtype: RecordService
        """
        return self.session.runtime.replay

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
    def workspace(self) -> WorkspaceService:
        """
        Workspace service.

        :return: Workspace service.
        :rtype: WorkspaceService
        """
        return self.session.runtime.workspace

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


def create_wrfrun_session() -> Token[WRFRunSession | None]:
    """
    Helper function to create new wrfrun session.

    :return: Session token
    :rtype: Token[WRFRunSession | None]
    """
    resource = ResourceCatalog()
    io = IOService(resource)
    registry = ExecutableRegistry()
    replay = ReplayService(resource, io, registry)
    runner = RunnerService(resource)
    workspace = WorkspaceService(resource, io)

    config = ConfigService(io, resource)
    namelist = NamelistService(io)
    states = WRFRunStates()

    wrfrun_session = WRFRunSession(
        runtime=RuntimeService(
            io=io,
            replay=replay,
            registry=registry,
            resource=resource,
            runner=runner,
            workspace=workspace,
        ),
        states=StatesService(
            config=config,
            namelist=namelist,
            states=states,
        ),
    )

    return WRFRUN_NEW.set_session(wrfrun_session)


__all__ = ["WRFRunVarAPI", "WRFRUN_NEW", "create_wrfrun_session"]
