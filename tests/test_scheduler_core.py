import sys
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from wrfrun.core.core import WRFRUN_NEW, create_wrfrun_session
from wrfrun.scheduler.core import detect_scheduler_job, prepare_scheduler_script, submit_scheduler_task
from wrfrun.scheduler.lsf import LSFBackend
from wrfrun.scheduler.pbs import PBSBackend
from wrfrun.scheduler.slurm import SlurmBackend


@pytest.mark.parametrize(
    ("configured_interpreter", "expected_interpreter"),
    [("", sys.executable), ("/custom/python", "/custom/python")],
)
def test_scheduler_script_uses_configured_or_current_python(
    tmp_path: Path,
    configured_interpreter: str,
    expected_interpreter: str,
):
    token = create_wrfrun_session()
    try:
        project = tmp_path / "project"
        WRFRUN_NEW.resource.register_default_providers(project, project / ".wrfrun", "common", "run-1")
        WRFRUN_NEW.config._config = {
            "core_num": 1,
            "job_scheduler": {
                "job_scheduler": "pbs",
                "queue_name": "",
                "node_num": 1,
                "env_settings": {},
                "python_interpreter": configured_interpreter,
            }
        }
        entry_file = project / "run.py"
        entry_file.parent.mkdir(parents=True)
        entry_file.write_text("pass\n")

        script = Path(prepare_scheduler_script(entry_file.as_posix())).read_text()

        assert f"{expected_interpreter} {entry_file}" in script
    finally:
        WRFRUN_NEW.reset_session(token)


@pytest.mark.parametrize(
    ("backend_type", "output", "expected_job_id"),
    [
        (LSFBackend, b"Job <12345> is submitted to queue <normal>.\n", "12345"),
        (PBSBackend, b"12345.server\n", "12345.server"),
        (SlurmBackend, b"12345;cluster\n", "12345"),
    ],
)
def test_scheduler_backend_submits_and_parses_job_id(monkeypatch, tmp_path, backend_type, output, expected_job_id):
    backend = backend_type()
    module = sys.modules[backend_type.__module__]
    submitted = []

    def fake_call(command, **kwargs):
        submitted.append((command, kwargs))
        return CompletedProcess(command, 0, stdout=output, stderr=b"")

    monkeypatch.setattr(module, "call_subprocess", fake_call)

    assert backend.submit(tmp_path / "submit.sh") == expected_job_id
    assert submitted


@pytest.mark.parametrize(
    ("backend_type", "environment_key"),
    [
        (LSFBackend, "LSB_JOBID"),
        (PBSBackend, "PBS_JOBID"),
        (SlurmBackend, "SLURM_JOB_ID"),
    ],
)
def test_scheduler_backend_detects_job_id(monkeypatch, backend_type, environment_key):
    backend = backend_type()

    monkeypatch.setenv(environment_key, "12345")

    assert backend.detect_job_id() == "12345"


@pytest.mark.parametrize("backend_type", [LSFBackend, PBSBackend, SlurmBackend])
def test_scheduler_backend_keeps_submission_when_job_id_is_unavailable(monkeypatch, tmp_path, backend_type, caplog):
    backend = backend_type()
    module = sys.modules[backend_type.__module__]

    monkeypatch.setattr(
        module,
        "call_subprocess",
        lambda command, **kwargs: CompletedProcess(command, 0, stdout=b"submitted\n", stderr=b"notice\n"),
    )

    assert backend.submit(tmp_path / "submit.sh") is None
    assert "Check whether the task was submitted" in caplog.text
    assert "submitted" in caplog.text


def test_scheduler_core_submits_and_detects_current_job(monkeypatch, tmp_path: Path):
    token = create_wrfrun_session()
    try:
        project = tmp_path / "project"
        WRFRUN_NEW.resource.register_default_providers(project, project / ".wrfrun", "common", "run-1")
        WRFRUN_NEW.config._config = {
            "core_num": 1,
            "job_scheduler": {
                "job_scheduler": "lsf",
                "queue_name": "",
                "node_num": 1,
                "env_settings": {},
                "python_interpreter": "",
            },
        }
        entry_file = project / "run.py"
        entry_file.parent.mkdir(parents=True)
        entry_file.write_text("pass\n")

        class Backend:
            name = "lsf"

            def submit(self, script_path):
                assert Path(script_path).is_file()
                return "12345"

            def detect_job_id(self):
                return "12345"

        monkeypatch.setattr("wrfrun.scheduler.core.get_scheduler_backend", lambda name: Backend())

        assert submit_scheduler_task(entry_file.as_posix()) == "12345"
        assert detect_scheduler_job() == {"backend": "lsf", "job_id": "12345"}
    finally:
        WRFRUN_NEW.reset_session(token)
