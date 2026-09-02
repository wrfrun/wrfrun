"""
wrfrun.workspace.arps
#####################

Functions to prepare workspace for ARPS model and its submodels.

.. autosummary::
    :toctree: generated/

    get_arps_workspace_path
    prepare_arps_workspace
"""

import logging
from os import symlink
from os.path import abspath, exists

from wrfrun.core import WRFRUN_NEW

from ..core.type import ResourceRef

LOGGER = logging.getLogger("wrfrun")


def prepare_arps_workspace(model_config: dict):
    """
    Initialize workspace for ARPS model and its submodels.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$WORKSPACE/model/ARPS/arps``
    2. ``$WORKSPACE/model/ARPS/{SUBMODEL_NAME}``

    :param model_config: Model config.
    :type model_config: dict
    """
    LOGGER.info("Initialize workspace for ARPS.")

    arps_bin_dir = model_config["global"]["arps_bin_directory"]
    submodel_name_list: list[str] = [x for x in model_config if x not in ("use", "global")]
    arps_bin_dir = abspath(arps_bin_dir)

    if not exists(arps_bin_dir):
        LOGGER.error("Your ARPS binary path ([magenta]arps_bin_directory[/magenta]) is wrong, check your TOML config.")
        raise FileNotFoundError("Your ARPS binary path (arps_bin_directory) is wrong, check your TOML config.")

    arps_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_arps", ""))

    for _submodel in submodel_name_list:
        if not exists(f"{arps_bin_dir}/{_submodel}"):
            LOGGER.warning(
                f"[magenta]{_submodel}[/magenta] not found in {arps_bin_dir}, mark it with [magenta]is_valid=False[/magenta]."
            )
            model_config.setdefault(_submodel, {})["is_valid"] = False

        else:
            _submodel_work_dir = arps_work_path / _submodel
            _submodel_work_dir.mkdir(exist_ok=True, parents=True)
            symlink(f"{arps_bin_dir}/{_submodel}", _submodel_work_dir / _submodel)
            model_config.setdefault(_submodel, {})["is_valid"] = True

    # arps core has two version: arps and arps_mpi, we also need to check arps_mpi
    if not exists(f"{arps_bin_dir}/arps_mpi"):
        LOGGER.warning(
            f"[magenta]arps_mpi[/magenta] not found in {arps_bin_dir}. "
            "If you want to run arps with MPI, make sure you have compiled MPI version of ARPS core."
        )
        model_config.setdefault("arps_mpi", {})["is_valid"] = False
    else:
        _arpsmpi_work_dir = arps_work_path / "arps_mpi"
        _arpsmpi_work_dir.mkdir(exist_ok=True, parents=True)
        symlink(f"{arps_bin_dir}/arps_mpi", _arpsmpi_work_dir / "arps_mpi")
        model_config.setdefault("arps_mpi", {})["is_valid"] = True


def check_arps_workspace(model_config: dict) -> bool:
    """
    Check that enabled ARPS executables have been staged in their workspaces.

    :param model_config: ARPS model configuration.
    :type model_config: dict
    :return: ``True`` when every enabled ARPS executable is available.
    :rtype: bool
    """
    arps_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_arps", ""))
    executable_names: list[str] = [name for name in model_config if name not in ("use", "global")]
    executable_names.append("arps_mpi")

    flag = True
    for executable_name in executable_names:
        executable_config = model_config.get(executable_name, {})
        if executable_config.get("is_valid") is False:
            continue

        executable_path = arps_work_path / executable_name / executable_name
        flag = flag & executable_path.is_file()

    return flag


__all__ = ["prepare_arps_workspace", "check_arps_workspace"]
