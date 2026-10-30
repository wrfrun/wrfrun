from pathlib import Path

import pytest

from wrfrun.core.runtime.resource import ResourceCatalog, RunLayout
from wrfrun.core.type import ResourceRef


def test_run_layout_uses_experiment_specific_paths(tmp_path: Path):
    layout = RunLayout.create(tmp_path / "project", tmp_path / "project/.wrfrun", "v01", "run-1")

    assert layout.input_dir == tmp_path / "project/data/inputs/experiments/v01"
    assert layout.output_dir == tmp_path / "project/data/outputs/v01/run-1"
    assert layout.results_dir == tmp_path / "project/data/outputs/v01/results"
    assert layout.workspace_dir == tmp_path / "project/.wrfrun/runs/v01/run-1/workspace"


def test_run_layout_uses_common_input_directory(tmp_path: Path):
    layout = RunLayout.create(tmp_path / "project", tmp_path / "project/.wrfrun", "common", "run-1")

    assert layout.input_dir == tmp_path / "project/data/inputs/common"


def test_resource_catalog_resolves_latest_and_specific_results(runtime):
    assert runtime.resource.get_result_ref("arps") == ResourceRef("results", "./arps")
    assert runtime.resource.get_result_ref("arps", "run-0") == ResourceRef(
        "project", "data/outputs/v01/run-0/arps"
    )


def test_publish_results_replaces_latest_result_link(runtime):
    first_archive = runtime.project / "data/outputs/v01/run-1/arps"
    first_archive.mkdir(parents=True)
    runtime.resource.publish_results("arps")

    result_link = runtime.project / "data/outputs/v01/results/arps"
    assert result_link.is_symlink()
    assert result_link.resolve() == first_archive

    newer_resource = ResourceCatalog()
    newer_resource.register_default_providers(runtime.project, runtime.project / ".wrfrun", "v01", "run-2")
    second_archive = runtime.project / "data/outputs/v01/run-2/arps"
    second_archive.mkdir(parents=True)
    newer_resource.publish_results("arps")

    assert result_link.is_symlink()
    assert result_link.resolve() == second_archive


def test_publish_results_replaces_normal_result_directory(runtime):
    archive = runtime.project / "data/outputs/v01/run-1/arps"
    archive.mkdir(parents=True)
    result_directory = runtime.project / "data/outputs/v01/results/arps"
    result_directory.mkdir(parents=True)

    runtime.resource.publish_results("arps")

    assert result_directory.is_symlink()
    assert result_directory.resolve() == archive


def test_resource_catalog_rejects_duplicate_and_unknown_providers(runtime):
    with pytest.raises(ValueError, match="already registered"):
        runtime.resource.register_provider("project", runtime.project)

    with pytest.raises(KeyError, match="Unknown resource provider"):
        runtime.resource.get_custom_resource(ResourceRef("missing", "file"))


def test_resource_catalog_requires_layout_before_access():
    resource = ResourceCatalog()

    with pytest.raises(RuntimeError, match="not initialized"):
        _ = resource.layout
