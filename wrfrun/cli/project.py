"""CLI handlers for project and model commands."""

import argparse
from os import listdir
from pathlib import Path

from ..core.operations.project import MODEL_MAP, add_models, initialize_project
from ..log import logger


def entry_init(args: argparse.Namespace):
    """Initialize a wrfrun project."""
    project_path = Path(args.path).resolve()
    if project_path.is_dir():
        files = listdir(project_path)
        excluded = {
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
        }
        if any(file_name not in excluded for file_name in files):
            logger.error(f"[CLI] {project_path} isn't empty, choose an empty directory, or backup and delete your files first.")
            exit(1)

    model_list = initialize_project(project_path, args.models)
    logger.info(f"Created project {project_path}.")
    if model_list:
        logger.info(f"Use the following models: {model_list}.")
    logger.info(f"All your configs should be placed in '{project_path}/configs'.")
    logger.info(f"All your data should be placed in '{project_path}/data'.")
    logger.info(f"All your namelist template files should be placed in '{project_path}/configs/namelists/templates'.")
    logger.info(f"All your namelist files should be placed in '{project_path}/configs/namelists/user'.")
    logger.info(f"Custom scheduler scripts should be placed in '{project_path}/configs/scheduler'.")
    logger.info(f"Make sure to set `[magenta]use = True[/]` to enable models in '{project_path}/config.toml' .")
    logger.info("It is recommanded to use git to track your wrfrun and model configs.")
    logger.info("Use command `[magenta]wrfrun add MODEL_NAME[/]` to add a new model to project.")


def entry_model(args: argparse.Namespace):
    """Add models to a wrfrun project."""
    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        logger.error(f"Can't find '{config_path}', initialize this project first.")
        exit(1)

    for model_name in args.add:
        if model_name not in MODEL_MAP:
            logger.error(f"Unknow model type: '{model_name}'")
            exit(1)

    add_models(config_path, args.add)
    logger.info(f"Added models: {args.add}")
