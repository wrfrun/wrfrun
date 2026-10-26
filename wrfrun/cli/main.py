"""Argument parser and entry point for the wrfrun command."""

import argparse
import sys

from ..core import create_wrfrun_session
from .experiment import entry_create
from .jobs import entry_jobs
from .profile import entry_load, entry_save
from .project import entry_init, entry_model

CLI_SESSION = create_wrfrun_session()


def main_entry():
    """Run the ``wrfrun`` command line interface."""
    args_parser = argparse.ArgumentParser()
    subparsers = args_parser.add_subparsers(title="Subcommands", description="Valid Subcommands", help="Subcommands")

    init_parser = subparsers.add_parser("init", help="Initialize a wrfrun project.", add_help=True)
    init_parser.add_argument("-p", "--path", type=str, default=".", help="Path of the wrfrun project.")
    init_parser.add_argument(
        "--models", nargs="*", type=str, help="List of models to use.", choices=["wrf", "palm", "roms", "arps"]
    )
    init_parser.set_defaults(func=entry_init)

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
    model_parser.set_defaults(func=entry_model)

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
    input_mode_group.add_argument("--copy", action="store_true", help="Copy common input files into the experiment.")
    experiment_create_parser.add_argument("-c", "--config", type=str, default="config.toml", help="Path of the main config file.")
    experiment_create_parser.set_defaults(func=entry_create)

    save_parser = subparsers.add_parser("save", help="Save a reusable configuration profile.", add_help=True)
    save_parser.add_argument("destination", nargs="?", help="Global profile name or ZIP file path.")
    save_parser.add_argument("-c", "--config", default="config.toml", help="Path of the main config file.")
    save_parser.add_argument("-e", "--experiment", default="common", help="Experiment to save.")
    save_parser.add_argument("--global", dest="global_profile", action="store_true", help="Use the local profile library.")
    save_parser.add_argument("-l", "--list", action="store_true", help="List profiles in the local profile library.")
    save_parser.add_argument("-r", "--remove", metavar="NAME", help="Remove a profile from the local profile library.")
    save_parser.set_defaults(func=entry_save)

    load_parser = subparsers.add_parser("load", help="Create a project from a saved profile.", add_help=True)
    load_parser.add_argument("source", help="Global profile name or ZIP file path.")
    load_parser.add_argument("-p", "--path", required=True, help="Path of the new project.")
    load_parser.add_argument("--global", dest="global_profile", action="store_true", help="Use the local profile library.")
    load_parser.set_defaults(func=entry_load)

    jobs_parser = subparsers.add_parser("jobs", help="List active simulation runs or follow command output.", add_help=True)
    jobs_parser.add_argument("-c", "--config", default="config.toml", help="Path of the main config file.")
    jobs_parser.add_argument("-f", "--follow", metavar="RUN_ID", help="Follow stdout from one run's current command.")
    jobs_parser.add_argument("--stream", choices=["stdout", "stderr"], default="stdout", help="Log stream to follow.")
    jobs_parser.set_defaults(func=entry_jobs)

    args = args_parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    args.func(args)


__all__ = ["main_entry"]
