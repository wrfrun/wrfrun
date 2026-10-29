from pathlib import Path

from wrfrun.core.runtime.io import IOService
from wrfrun.core.runtime.resource import ResourceCatalog
from wrfrun.core.states.config import ConfigService, _merge_config


def test_merge_config_applies_nested_overrides_without_mutating_base():
    base = {"model": {"demo": {"use": True, "settings": {"kept": 1, "changed": 1}}}}
    override = {"model": {"demo": {"settings": {"changed": 2, "added": 3}}}}

    merged = _merge_config(base, override)

    assert merged == {"model": {"demo": {"use": True, "settings": {"kept": 1, "changed": 2, "added": 3}}}}
    assert base["model"]["demo"]["settings"] == {"kept": 1, "changed": 1}


def test_config_service_expands_models_before_experiment_overrides(tmp_path: Path, monkeypatch):
    project = tmp_path / "project"
    config_path = project / "config.toml"
    include_path = project / "models/demo.toml"
    experiment_path = project / "configs/experiments/v01/experiment.toml"
    include_path.parent.mkdir(parents=True)
    experiment_path.parent.mkdir(parents=True)
    config_path.write_text('work_dir = ".wrfrun"\n[model.demo]\nuse = true\ninclude = "models/demo.toml"\n')
    include_path.write_text("[settings]\nkept = 1\nchanged = 1\n")
    experiment_path.write_text("[model.demo.settings]\nchanged = 2\nadded = 3\n")

    class Plugin:
        name = "demo"

        def register(self):
            return None

    monkeypatch.setattr("wrfrun.model.plugins.load_model_plugin", lambda _: Plugin())
    resource = ResourceCatalog()
    config = ConfigService(IOService(resource), resource)
    config.load_wrfrun_config(config_path.as_posix(), experiment="v01", run_id="run-1")

    assert config.get_model_config("demo") == {"use": True, "settings": {"kept": 1, "changed": 2, "added": 3}}
    assert resource.layout.experiment == "v01"
    assert resource.layout.run_id == "run-1"
    assert resource.layout.workspace_dir == project / ".wrfrun/runs/v01/run-1/workspace"
