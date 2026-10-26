"""CLI handlers for experiment commands."""

import argparse
from pathlib import Path

from ..core.operations.experiment import create_experiment
from ..log import logger


def entry_create(args: argparse.Namespace):
    """Create a new experiment skeleton."""
    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        logger.error(f"Can't find '{config_path}', initialize this project first.")
        exit(1)

    if Path(args.name).name != args.name or args.name in (".", ".."):
        logger.error("Experiment name must be a single directory name.")
        exit(1)

    experiment_dir = config_path.parent / "configs/experiments" / args.name
    if experiment_dir.exists():
        logger.error(f"Experiment '{args.name}' already exists.")
        exit(1)

    create_experiment(config_path, args.name, args.copy)
    input_mode = "copied" if args.copy else "symlinked"
    logger.info(f"Created experiment '{args.name}' with {input_mode} inputs.")
