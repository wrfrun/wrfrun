"""CLI handlers for reusable profile commands."""

import argparse
from pathlib import Path

from rich.table import Table

from ..core.operations.profile import get_global_profile_path, list_profiles, load_profile, remove_global_profile, save_profile
from ..log import get_wrfrun_rich_console, logger


def entry_save(args: argparse.Namespace):
    """Save an experiment configuration as a reusable profile."""
    if args.remove is not None:
        if args.destination is not None or args.list:
            logger.error("--remove cannot be combined with a destination or --list.")
            exit(1)

        remove_global_profile(args.remove)
        logger.info(f"Removed global profile '{args.remove}'.")
        return

    if args.list:
        if args.destination is not None:
            logger.error("A profile destination cannot be used with --list.")
            exit(1)

        table = Table(title="Saved wrfrun profiles")
        table.add_column("Name", style="cyan")
        table.add_column("Experiment")
        table.add_column("Models")
        table.add_column("Created at")
        for profile in list_profiles():
            table.add_row(profile.name, profile.experiment, ", ".join(profile.models), profile.created_at)
        get_wrfrun_rich_console().print(table)
        return

    if args.destination is None:
        logger.error("A profile destination is required unless --list is used.")
        exit(1)

    archive_path = get_global_profile_path(args.destination) if args.global_profile else Path(args.destination)
    save_profile(args.config, args.experiment, archive_path)
    logger.info(f"Saved profile to '{archive_path.resolve()}'.")


def entry_load(args: argparse.Namespace):
    """Create a new project from a saved profile."""
    archive_path = get_global_profile_path(args.source) if args.global_profile else Path(args.source)
    load_profile(archive_path, args.path)
    logger.info(f"Created project '{Path(args.path).resolve()}' from '{archive_path.resolve()}'.")
