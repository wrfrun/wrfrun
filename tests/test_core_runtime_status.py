import json

from wrfrun.core.runtime.status import RunStatusService


def test_status_service_persists_lifecycle(runtime):
    service = RunStatusService(runtime.resource)
    stdout = runtime.project / "logs/stdout.txt"
    stderr = runtime.project / "logs/stderr.txt"

    service.start()
    service.start_command("arps", ("./arps",), stdout, stderr)
    service.finish_command(0)
    service.finish()

    status = json.loads(service.path.read_text())
    assert service.state == "succeeded"
    assert status["experiment"] == "v01"
    assert status["run_id"] == "run-1"
    assert status["current_executable"] == "arps"
    assert status["command"] == ["./arps"]
    assert status["returncode"] == 0
    assert status["finished_at"] is not None


def test_status_service_records_failure(runtime):
    service = RunStatusService(runtime.resource)
    service.start()
    service.fail("command failed", returncode=2, timed_out=True)

    status = json.loads(service.path.read_text())
    assert service.state == "failed"
    assert status["error"] == "command failed"
    assert status["returncode"] == 2
    assert status["timed_out"] is True
