import sys
from pathlib import Path

import pytest

from wrfrun.core.core import WRFRUN_NEW, create_wrfrun_session
from wrfrun.scheduler.core import prepare_scheduler_script


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
