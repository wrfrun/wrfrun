"""
wrfrun.core.operations.experiment
#################################

Create experiment-specific project files and inputs.

.. autosummary::
    :toctree: generated/

    create_experiment
"""

from os.path import relpath
from pathlib import Path
from shutil import copy2

import tomli

from ...model.plugins import load_model_plugin
from ...res import CONFIG_EXPERIMENT_TOML_TEMPLATE
from ..core import WRFRUN_NEW
from .project import MODEL_MAP


def _stage_experiment_inputs(source_dir: Path, target_dir: Path, copy: bool):
    """Create an experiment input tree from common inputs."""
    for source_path in source_dir.rglob("*"):
        target_path = target_dir / source_path.relative_to(source_dir)

        if source_path.is_dir():
            target_path.mkdir(exist_ok=True)
        else:
            target_path.parent.mkdir(exist_ok=True, parents=True)
            if copy:
                copy2(source_path, target_path)
            else:
                target_path.symlink_to(relpath(source_path, target_path.parent))


def create_experiment(config_path: str | Path, name: str, copy: bool = False):
    """Create configuration, input, output, and runtime directories for one experiment."""
    config_path = Path(config_path).resolve()
    project_path = config_path.parent
    experiment_config_dir = project_path / "configs/experiments" / name

    WRFRUN_NEW.io.copy(
        file_path=CONFIG_EXPERIMENT_TOML_TEMPLATE,
        save_path=experiment_config_dir / "experiment.toml",
    )
    (experiment_config_dir / "namelists").mkdir(parents=True)
    (experiment_config_dir / "scheduler").mkdir(parents=True)

    with config_path.open("rb") as config_handle:
        main_config = tomli.load(config_handle)

    for model_name, model_config in main_config["model"].items():
        if model_name in MODEL_MAP and model_config["use"]:
            load_model_plugin(model_name).initialize_experiment_files(experiment_config_dir)

    common_input_dir = project_path / "data/inputs/common"
    experiment_input_dir = project_path / "data/inputs/experiments" / name
    common_input_dir.mkdir(exist_ok=True, parents=True)
    experiment_input_dir.mkdir(parents=True)
    _stage_experiment_inputs(common_input_dir, experiment_input_dir, copy)
    (project_path / "data/outputs" / name).mkdir(parents=True)
    (project_path / "logs" / name).mkdir(parents=True)
    (project_path / ".wrfrun/runs" / name).mkdir(parents=True)


__all__ = ["create_experiment"]
