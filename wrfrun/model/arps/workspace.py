"""
wrfrun.model.arps.workspace
###########################

Functions to prepare workspace for ARPS model and its submodels.

.. autosummary::
    :toctree: generated/

    prepare_arps_workspace
    check_arps_workspace
"""

import logging
from pathlib import Path

from wrfrun.core import WRFRUN_NEW
from wrfrun.core.type import ResourceRef

LOGGER = logging.getLogger("wrfrun")


def prepare_arps_workspace():
    """
    Initialize workspace for ARPS model and its submodels.

    This function will check following paths,
    and create them or delete old files inside:

    1. ``$WORKSPACE/model/ARPS/arps``
    2. ``$WORKSPACE/model/ARPS/{SUBMODEL_NAME}``
    """
    LOGGER.info("Initialize workspace for ARPS.")

    model_config = WRFRUN_NEW.config.get_model_config("arps")

    arps_bin_dir = Path(model_config["global"]["arps_bin_directory"]).resolve()
    submodel_name_list: list[str] = [x for x in model_config if x not in ("use", "global")]

    if not arps_bin_dir.is_dir():
        LOGGER.error("Your ARPS binary path ([magenta]arps_bin_directory[/magenta]) is wrong, check your TOML config.")
        raise FileNotFoundError("Your ARPS binary path (arps_bin_directory) is wrong, check your TOML config.")

    arps_work_path = WRFRUN_NEW.resource.get_custom_resource(ResourceRef("workspace_arps", ""))

    for _submodel in submodel_name_list:
        if not (arps_bin_dir / _submodel).is_file():
            LOGGER.warning(
                f"[magenta]{_submodel}[/magenta] not found in {arps_bin_dir}, mark it with [magenta]is_valid=False[/magenta]."
            )
            model_config.setdefault(_submodel, {})["is_valid"] = False

        else:
            WRFRUN_NEW.io.symlink(
                file_path=arps_bin_dir / _submodel,
                save_path=arps_work_path / _submodel / _submodel,
            )
            model_config.setdefault(_submodel, {})["is_valid"] = True

    # arps core has two version: arps and arps_mpi, we also need to check arps_mpi
    if not (arps_bin_dir / "arps_mpi").is_file():
        LOGGER.warning(
            f"[magenta]arps_mpi[/magenta] not found in {arps_bin_dir}. "
            "If you want to run arps with MPI, make sure you have compiled MPI version of ARPS core."
        )
        model_config.setdefault("arps_mpi", {})["is_valid"] = False
    else:
        WRFRUN_NEW.io.symlink(
            file_path=arps_bin_dir / "arps_mpi",
            save_path=arps_work_path / "arps_mpi/arps_mpi",
        )
        model_config.setdefault("arps_mpi", {})["is_valid"] = True


def check_arps_workspace() -> bool:
    """
    Check that enabled ARPS executables have been staged in their workspaces.

    :return: ``True`` when every enabled ARPS executable is available.
    :rtype: bool
    """
    model_config = WRFRUN_NEW.config.get_model_config("arps")

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
