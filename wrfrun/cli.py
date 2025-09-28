import argparse
import sys
from os import getcwd, makedirs
from os.path import exists
from shutil import copyfile

from .core import WRFRUNConfig
from .res import CONFIG_MAIN_TOML_TEMPLATE, CONFIG_WRF_TOML_TEMPLATE
from .utils import logger


MODEL_MAP = {
    "wrf": CONFIG_WRF_TOML_TEMPLATE
}


def _entry_init(args: argparse.Namespace):
    """
    Initialize a wrfrun project.

    :param args: Arguments namespace.
    :type args: argparse.Namespace
    """
    args = vars(args)

    project_name = args["name"]
    models = args["models"]

    if exists(project_name):
        logger.error(f"{project_name} already exists.")
        exit(1)

    makedirs(f"{project_name}/configs")
    makedirs(f"{project_name}/data")

    copyfile(WRFRUNConfig.parse_resource_uri(CONFIG_MAIN_TOML_TEMPLATE), f"{project_name}/config.toml")

    for _model in models:
        src_path = WRFRUNConfig.parse_resource_uri(MODEL_MAP[_model])
        copyfile(src_path, f"{project_name}/configs/{_model}.toml")

    logger.info(f"Created project {project_name}.")
    logger.info(f"Use command `wrfrun add MODEL_NAME` to add a new model to project.")


def _entry_model(args: argparse.Namespace):
    """
    Manage models used by wrfrun project.

    :param args: Arguments namespace.
    :type args: argparse.Namespace
    """
    pass


def main_entry():
    """
    CLI entry point.
    """

    args_parser = argparse.ArgumentParser()
    subparsers = args_parser.add_subparsers(title="Subcommands", description="Valid Subcommands", help="Subcommands")

    init_parser = subparsers.add_parser("init", help="Initialize a wrfrun project.", add_help=True)
    init_parser.add_argument("-n", "--name", type=str, required=True, help="Name of the wrfrun project.")
    init_parser.add_argument("--models", nargs="*", type=str, help="List of models to use.", choices=["wrf"])
    init_parser.set_defaults(func=_entry_init)

    model_parser = subparsers.add_parser("model", help="Manage models used by wrfrun project.", add_help=True)
    model_parser.add_argument("add", type="str", help="Add a model to the project.")
    model_parser.set_defaults(func=_entry_model)

    args = args_parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    args.func(args)


__all__ = ["main_entry"]
