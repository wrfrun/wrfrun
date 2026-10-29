import sys
from pathlib import Path

import pytest

from wrfrun.core.error import CommandExecutionError
from wrfrun.core.runtime.runner import Command, CommandStdStream, RunnerService, StreamMode
from wrfrun.core.type import ResourceRef


def test_runner_captures_standard_streams(runtime):
    command = Command.from_args(
        [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"]
    )

    result = RunnerService(runtime.resource).run(command)

    assert result.succeeded
    assert result.stdout == "out\n"
    assert result.stderr == "err\n"
    assert result.duration_seconds >= 0


def test_runner_writes_streams_and_reads_stdin(runtime):
    stdin = runtime.project / "input.txt"
    stdin.parent.mkdir(parents=True)
    stdin.write_text("input data")
    command = Command.from_args(
        [sys.executable, "-c", "import sys; print(sys.stdin.read())"],
        stdin_path=ResourceRef("project", "input.txt"),
        stdout=CommandStdStream(StreamMode.FILE, ResourceRef("project", "logs/stdout.txt")),
        stderr=CommandStdStream(StreamMode.FILE, ResourceRef("project", "logs/stderr.txt")),
    )

    result = RunnerService(runtime.resource).run(command)

    assert result.succeeded
    assert result.stdout is None
    assert result.stderr is None
    assert (runtime.project / "logs/stdout.txt").read_text() == "input data\n"
    assert (runtime.project / "logs/stderr.txt").read_text() == ""


def test_runner_supports_a_clean_environment(runtime):
    command = Command.from_args(
        [sys.executable, "-c", "import os; print(os.environ['WRFRUN_TEST_FLAG'])"],
        environment={"WRFRUN_TEST_FLAG": "enabled"},
        inherit_environment=False,
    )

    result = RunnerService(runtime.resource).run(command)

    assert result.succeeded
    assert result.stdout == "enabled\n"


def test_runner_reports_failures_and_timeouts(runtime):
    runner = RunnerService(runtime.resource)
    failed = runner.run(Command.from_args([sys.executable, "-c", "raise SystemExit(3)"]))
    timed_out = runner.run(Command.from_args([sys.executable, "-c", "import time; time.sleep(10)"], timeout_seconds=0.1))

    assert failed.returncode == 3
    with pytest.raises(CommandExecutionError):
        failed.require_success()
    assert timed_out.timed_out
    assert not timed_out.succeeded


def test_command_and_runner_reject_invalid_inputs(runtime):
    with pytest.raises(ValueError):
        Command.from_args([])
    with pytest.raises(ValueError):
        CommandStdStream(StreamMode.FILE)
    with pytest.raises(NotADirectoryError):
        RunnerService(runtime.resource).run(Command.from_args([sys.executable, "-c", "pass"], cwd="missing"))
    with pytest.raises(FileNotFoundError):
        RunnerService(runtime.resource).run(
            Command.from_args([sys.executable, "-c", "pass"], stdin_path=Path("missing-input.txt"))
        )
