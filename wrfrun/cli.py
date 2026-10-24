"""
wrfrun.cli
##########

.. autosummary::
    :toctree: generated/

    main_entry

``wrfrun`` command line interface (CLI).

**This is an experimental tool, NOT BEING STABLE YET.**

After installing ``wrfrun``, you can use command ``wrfrun`` to create a simulation project.
Get more information by running ``wrfrun --help``.
"""

import argparse
import sys
from os import listdir
from os.path import relpath
from pathlib import Path
from shutil import copy2

import tomli
import tomli_w

from .core import PROJECT_TREE, WRFRUN_NEW, create_wrfrun_session
from .log import logger
from .model.plugins import load_model_plugin
from .res import (
    CONFIG_ARPS_TOML_TEMPLATE,
    CONFIG_EXPERIMENT_TOML_TEMPLATE,
    CONFIG_MAIN_TOML_TEMPLATE,
    CONFIG_PALM_TOML_TEMPLATE,
    CONFIG_ROMS_TOML_TEMPLATE,
    CONFIG_WRF_TOML_TEMPLATE,
    GITIGNORE_RULES,
)

MODEL_MAP = {
    "arps": CONFIG_ARPS_TOML_TEMPLATE,
    "wrf": CONFIG_WRF_TOML_TEMPLATE,
    "palm": CONFIG_PALM_TOML_TEMPLATE,
    "roms": CONFIG_ROMS_TOML_TEMPLATE,
}

CLI_SESSION = create_wrfrun_session()


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


def _entry_init(args: argparse.Namespace):
    """
    Initialize a wrfrun project.

    :param args: Arguments namespace.
    :type args: argparse.Namespace
    """
    configs = vars(args)

    project_path = Path(configs["path"]).resolve()
    models = configs["models"]

    if project_path.is_dir():
        # we need to check if this directory isn't empty.
        files = listdir(project_path)
        # exclude:
        exclude_target = [
            ".venv",
            ".git",
            ".gitattribute",
            ".python-version",
            "pyproject.toml",
            "uv.lock",
            "configs",
            "data",
            "logs",
            ".wrfrun",
            "config.toml",
            ".gitignore",
        ]
        files = [x for x in files if x not in exclude_target]

        if len(files) != 0:
            logger.error(f"[CLI] {project_path} isn't empty, choose an empty directory, or backup and delete your files first.")
            exit(1)

    for directory in PROJECT_TREE:
        (project_path / directory).mkdir(exist_ok=True, parents=True)

    WRFRUN_NEW.io.copy(file_path=CONFIG_MAIN_TOML_TEMPLATE, save_path=project_path / "config.toml")
    WRFRUN_NEW.io.copy(file_path=GITIGNORE_RULES, save_path=project_path / ".gitignore")

    model_list = []
    if models is not None:
        for _model in models:
            if _model in MODEL_MAP:
                WRFRUN_NEW.io.copy(file_path=MODEL_MAP[_model], save_path=project_path / f"configs/{_model}.toml")
                load_model_plugin(_model).initialize_project_files(project_path)
                (project_path / "data/inputs/common" / _model).mkdir(exist_ok=True)
                model_list.append(_model)

            else:
                logger.warning(f"Unknown model: '{_model}'")

    logger.info(f"Created project {project_path}.")
    if len(model_list) > 0:
        logger.info(f"Use the following models: {model_list}.")
    logger.info(f"All your configs should be placed in '{project_path}/configs'.")
    logger.info(f"All your data should be placed in '{project_path}/data'.")
    logger.info(f"All your namelist template files should be placed in '{project_path}/configs/namelists/templates'.")
    logger.info(f"All your namelist files should be placed in '{project_path}/configs/namelists/user'.")
    logger.info(f"Make sure to set `[magenta]use = True[/]` to enable models in '{project_path}/config.toml' .")
    logger.info("It is recommanded to use git to track your wrfrun and model configs.")
    logger.info("Use command `[magenta]wrfrun add MODEL_NAME[/]` to add a new model to project.")


def _entry_model(args: argparse.Namespace):
    """
    Manage models used by wrfrun project.

    :param args: Arguments namespace.
    :type args: argparse.Namespace
    """
    configs = vars(args)
    new_models = configs["add"]
    config_path = Path(configs["config"]).resolve()
    project_path = config_path.parent

    if not config_path.is_file():
        logger.error(f"Can't find '{config_path}', initialize this project first.")
        exit(1)

    for _new_model in new_models:
        if _new_model not in MODEL_MAP:
            logger.error(f"Unknow model type: '{_new_model}'")
            exit(1)

    config_dir_path = config_path.parent / "configs"
    config_dir_path.mkdir(exist_ok=True, parents=True)

    with open(config_path, "rb") as f:
        main_config = tomli.load(f)

    for _new_model in new_models:
        if _new_model not in main_config["model"]:
            main_config["model"][_new_model] = {
                "note": (
                    "Config of this model is generated by wrfrun cli command. "
                    "DO NOT ADD CUSTOM CONFIG IN THIS SECTION because they may be overwrite by wrfrun cli tools."
                ),
                "use": True,
                "include": f"./configs/{_new_model}.toml",
            }

        else:
            if not ("use" in main_config["model"] and main_config["model"]["use"]):
                main_config["model"][_new_model] = {
                    "note": (
                        "Config of this model is generated by wrfrun cli command. "
                        "DO NOT ADD CUSTOM CONFIG IN THIS SECTION because they may be overwrite by wrfrun cli tools."
                    ),
                    "use": True,
                    "include": f"./configs/{_new_model}.toml",
                }

    for _new_model in new_models:
        WRFRUN_NEW.io.copy(file_path=MODEL_MAP[_new_model], save_path=config_dir_path / f"{_new_model}.toml")
        load_model_plugin(_new_model).initialize_project_files(project_path)
        (project_path / "data/inputs/common" / _new_model).mkdir(exist_ok=True)

    with open(config_path, "wb") as f:
        tomli_w.dump(main_config, f)

    logger.info(f"Added models: {new_models}")


def _entry_experiment_create(args: argparse.Namespace):
    """Create a new experiment skeleton."""
    config_path = Path(args.config).resolve()
    project_path = config_path.parent
    experiment_name = args.name

    if not config_path.is_file():
        logger.error(f"Can't find '{config_path}', initialize this project first.")
        exit(1)

    if Path(experiment_name).name != experiment_name or experiment_name in (".", ".."):
        logger.error("Experiment name must be a single directory name.")
        exit(1)

    experiment_config_dir = project_path / "configs/experiments" / experiment_name
    if experiment_config_dir.exists():
        logger.error(f"Experiment '{experiment_name}' already exists.")
        exit(1)

    WRFRUN_NEW.io.copy(
        file_path=CONFIG_EXPERIMENT_TOML_TEMPLATE,
        save_path=experiment_config_dir / "experiment.toml",
    )
    (experiment_config_dir / "namelists").mkdir(parents=True)
    common_input_dir = project_path / "data/inputs/common"
    experiment_input_dir = project_path / "data/inputs/experiments" / experiment_name
    common_input_dir.mkdir(exist_ok=True, parents=True)
    experiment_input_dir.mkdir(parents=True)
    _stage_experiment_inputs(common_input_dir, experiment_input_dir, args.copy)
    (project_path / "data/outputs" / experiment_name).mkdir(parents=True)
    (project_path / "logs" / experiment_name).mkdir(parents=True)
    (project_path / ".wrfrun/runs" / experiment_name).mkdir(parents=True)

    input_mode = "copied" if args.copy else "symlinked"
    logger.info(f"Created experiment '{experiment_name}' with {input_mode} inputs.")


def main_entry():
    """
    CLI entry point.
    """
    args_parser = argparse.ArgumentParser()
    subparsers = args_parser.add_subparsers(title="Subcommands", description="Valid Subcommands", help="Subcommands")

    init_parser = subparsers.add_parser("init", help="Initialize a wrfrun project.", add_help=True)
    init_parser.add_argument("-p", "--path", type=str, default=".", help="Path of the wrfrun project.")
    init_parser.add_argument(
        "--models",
        nargs="*",
        type=str,
        help="List of models to use.",
        choices=["wrf", "palm", "roms", "arps"],
    )
    init_parser.set_defaults(func=_entry_init)

    model_parser = subparsers.add_parser("model", help="Manage models used by wrfrun project.", add_help=True)
    model_parser.add_argument("-c", "--config", type=str, default="config.toml", help="Path of the main config file.")
    model_parser.add_argument(
        "-a",
        "--add",
        nargs="+",
        required=True,
        type=str,
        help="Add models to the project.",
        choices=["wrf", "palm", "roms", "arps"],
    )
    model_parser.set_defaults(func=_entry_model)

    experiment_parser = subparsers.add_parser("experiment", help="Manage project experiments.", add_help=True)
    experiment_subparsers = experiment_parser.add_subparsers(title="Experiment commands", required=True)
    experiment_create_parser = experiment_subparsers.add_parser("create", help="Create an experiment skeleton.", add_help=True)
    experiment_create_parser.add_argument("name", type=str, help="Name of the new experiment.")
    input_mode_group = experiment_create_parser.add_mutually_exclusive_group()
    input_mode_group.add_argument(
        "--symlink",
        action="store_false",
        dest="copy",
        help="Create relative symbolic links to common inputs (default).",
    )
    input_mode_group.add_argument(
        "--copy",
        action="store_true",
        help="Copy common input files into the experiment.",
    )
    experiment_create_parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.toml",
        help="Path of the main config file.",
    )
    experiment_create_parser.set_defaults(func=_entry_experiment_create)

    args = args_parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    args.func(args)


__all__ = ["main_entry"]
