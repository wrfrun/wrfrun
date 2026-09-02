"""
wrfrun.core.runtime.runner
##########################

External command runner.

.. autosummary::
    :toctree: generated/


"""

import os
import signal
import subprocess
import time
from contextlib import ExitStack
from dataclasses import dataclass
from enum import Enum
from os import fspath
from pathlib import Path
from shlex import join
from typing import Mapping, Sequence

from ..error import CommandExecutionError
from ..type import ResourceRef
from .resource import ResourceCatalog


class StreamMode(str, Enum):
    """Choose where a command's standard stream is sent."""

    CAPTURE = "capture"
    """Keep the stream in :class:`CommandResult`."""

    DISCARD = "discard"
    """Discard the stream by redirecting it to ``os.devnull``."""

    FILE = "file"
    """Write the stream to :attr:`StreamSpec.path`."""


@dataclass(frozen=True)
class CommandStdStream:
    """Describe where a command's standard output or error is written."""

    mode: StreamMode = StreamMode.CAPTURE
    path: str | ResourceRef | None = None

    def __post_init__(self):
        """
        Post initialization.

        :raises ValueError: Stream mode is file but file path isn't given.
        :raises ValueError: Stream mode isn't file but file path is given.
        """
        if self.mode is StreamMode.FILE and self.path is None:
            raise ValueError("StreamMode.FILE requires a path.")

        if self.mode is not StreamMode.FILE and self.path is not None:
            raise ValueError("Only StreamMode.FILE accepts a path.")


@dataclass(frozen=True)
class Command:
    """
    Describe one command independently of when it is executed.

    Use an argument vector rather than a shell command.  This keeps arguments,
    paths, standard streams, and timeout settings together for reuse and
    testing.

    **Example**

    >>> command = Command.from_args(["model.exe", "--dry-run"])
    >>> command.argv
    ('model.exe', '--dry-run')

    """

    argv: tuple[str, ...]
    cwd: str | ResourceRef | None = None
    stdin_path: str | ResourceRef | None = None
    stdout: CommandStdStream = CommandStdStream()
    stderr: CommandStdStream = CommandStdStream()
    environment: Mapping[str, str] | None = None
    inherit_environment: bool = True
    timeout_seconds: float | None = None

    @classmethod
    def from_args(
        cls,
        argv: Sequence[str | Path],
        **kwargs,
    ) -> "Command":
        """
        Create a validated specification from command arguments.

        :param argv: List of command name and arguments.
        :type argv: Sequence[str | Path]
        :return: Command.
        :rtype: Command.
        """
        normalized_argv = tuple(fspath(argument) for argument in argv)

        if not normalized_argv:
            raise ValueError("Command argv cannot be empty.")

        if any(not argument for argument in normalized_argv):
            raise ValueError("Command argv cannot contain empty arguments.")

        return cls(argv=normalized_argv, **kwargs)

    def __post_init__(self):
        """
        Post initialization.

        :raises ValueError: Command argv not given.
        :raises ValueError: Timeout value is negative.
        """
        if not self.argv:
            raise ValueError("Command argv cannot be empty.")

        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive when provided.")


@dataclass(frozen=True)
class CommandResult:
    """
    Record a command's exit status, output, and elapsed time.
    """

    command: Command
    returncode: int
    stdout: str | None
    stderr: str | None
    started_at: float
    finished_at: float
    timed_out: bool = False

    @property
    def duration_seconds(self) -> float:
        """Return the command duration in seconds."""
        return self.finished_at - self.started_at

    @property
    def succeeded(self) -> bool:
        """Return whether the command completed with exit status zero."""
        return not self.timed_out and self.returncode == 0

    def require_success(self) -> "CommandResult":
        """Return this result or raise :class:`CommandExecutionError`."""
        if not self.succeeded:
            raise CommandExecutionError(self)

        return self


class RunnerService:
    """
    External command runner service.
    """

    def __init__(self, resource: ResourceCatalog, timeout: float | None = None):
        """
        External command runner service.

        :param resource: Resource manager service.
        :type resource: ResourceCatalog
        :param timeout: Timeout seconds of the external command, defaults to None
        :type timeout: float | None, optional
        :raises ValueError: Timeout is negative.
        """
        self._resource = resource

        if isinstance(timeout, float) and timeout <= 0:
            raise ValueError("Timeout must be positive.")

        self.timeout = timeout

    def run(self, command: Command) -> CommandResult:
        """
        Run ``spec`` and return its result.

        Invalid paths and an unavailable executable raise an exception. A
        started command always returns a result, including timeout and non-zero
        exit cases.
        """
        cwd = self._validate_cwd(command.cwd)
        stdin_path = self._validate_stdin_path(command.stdin_path)
        environment = self._build_environment(command)
        started_at = time.monotonic()

        with ExitStack() as stack:
            stdin_file = stack.enter_context(stdin_path.open("rb")) if stdin_path is not None else None
            stdout_target = self._open_stream(stack, command.stdout)
            stderr_target = self._open_stream(stack, command.stderr)

            try:
                process = subprocess.Popen(
                    command.argv,
                    cwd=cwd,
                    stdin=stdin_file,
                    stdout=stdout_target,
                    stderr=stderr_target,
                    env=environment,
                    shell=False,
                    start_new_session=(os.name == "posix"),
                )
            except OSError as exc:
                raise CommandExecutionError(f"Failed to start command: {join(command.argv)}") from exc

            try:
                stdout_bytes, stderr_bytes = process.communicate(timeout=command.timeout_seconds)
                timed_out = False
            except subprocess.TimeoutExpired:
                self._terminate(process)
                stdout_bytes, stderr_bytes = process.communicate()
                timed_out = True

        finished_at = time.monotonic()

        return CommandResult(
            command=command,
            returncode=process.returncode,
            stdout=self._decode(stdout_bytes) if command.stdout.mode is StreamMode.CAPTURE else None,
            stderr=self._decode(stderr_bytes) if command.stderr.mode is StreamMode.CAPTURE else None,
            started_at=started_at,
            finished_at=finished_at,
            timed_out=timed_out,
        )

    def _validate_cwd(self, cwd: str | ResourceRef | None) -> Path | None:
        if cwd is None:
            return None

        if isinstance(cwd, ResourceRef):
            _cwd = self._resource.get_custom_resource(cwd)

        else:
            _cwd = Path(cwd)

        real_cwd = _cwd.expanduser().resolve()

        if not real_cwd.is_dir():
            raise NotADirectoryError(f"Command working directory does not exist: {real_cwd}")

        return real_cwd

    def _validate_stdin_path(self, stdin_path: str | ResourceRef | None) -> Path | None:
        if stdin_path is None:
            return None

        if isinstance(stdin_path, ResourceRef):
            _stdin_path = self._resource.get_custom_resource(stdin_path)

        else:
            _stdin_path = Path(stdin_path)

        real_stdin_path = _stdin_path.expanduser().resolve()

        if not real_stdin_path.is_file():
            raise FileNotFoundError(f"Command stdin file does not exist: {real_stdin_path}")

        return real_stdin_path

    @staticmethod
    def _build_environment(command: Command) -> dict[str, str] | None:
        if command.environment is None and command.inherit_environment:
            return None

        environment = dict(os.environ) if command.inherit_environment else {}

        if command.environment is not None:
            environment.update(command.environment)

        return environment

    def _open_stream(self, stack: ExitStack, command_stream: CommandStdStream):
        if command_stream.mode is StreamMode.CAPTURE:
            return subprocess.PIPE

        if command_stream.mode is StreamMode.DISCARD:
            return subprocess.DEVNULL

        assert command_stream.mode is StreamMode.FILE
        assert command_stream.path is not None

        if isinstance(command_stream.path, ResourceRef):
            path = self._resource.get_custom_resource(command_stream.path)
        else:
            path = Path(command_stream.path)

        path = path.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return stack.enter_context(path.open("wb"))

    def _terminate(self, process: subprocess.Popen[bytes]) -> None:
        """Terminate a timed-out process."""
        if os.name != "posix":
            process.terminate()
        else:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                return

        try:
            process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            if os.name != "posix":
                process.kill()
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    return

    @staticmethod
    def _decode(output: bytes | None) -> str:
        return "" if output is None else output.decode(errors="replace")


__all__ = ["StreamMode", "CommandStdStream", "Command", "CommandResult", "RunnerService"]
