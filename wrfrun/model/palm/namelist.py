"""
wrfrun.model.palm.namelist
##########################

Functions to process namelist for ``PALM``.

.. autosummary::
    :toctree: generated/

    prepare_palm_namelist
"""

import math
from os.path import exists

from wrfrun.core import WRFRUN
from wrfrun.log import logger

from .utils import find_optimal_grid_number, is_valid_palm_dimension


def prepare_palm_namelist():
    """
    This function loads user PALM namelist file and save it in :doc:`WRFRUN </api/core.core>`.
    """
    palm_config = WRFRUN.config.get_model_config("palm")
    namelist_file = palm_config["user_namelist"]

    if not exists(namelist_file):
        logger.error(f"Can't find PALM namelist: {namelist_file}")
        raise FileNotFoundError(f"Can't find PALM namelist: {namelist_file}")

    WRFRUN.config.read_namelist(namelist_file, "palm")


def get_namelist_save_name() -> str:
    """
    Get the save name of namelist file.

    :raises KeyError: Unknown simulation type set in config file.
    :return: Save name.
    :rtype: str
    """
    map_dict = {"d3#": "_p3d", "d3r": "_p3dr", "pcr": "_pcr"}

    config = WRFRUN.config.get_model_config("palm")
    simulation_type = config["simulation_type"]
    job_name = config["job_name"]

    if simulation_type in map_dict:
        return f"{job_name}{map_dict[simulation_type]}"

    logger.error(f"Unknown simulation type: Expect {tuple(map_dict.keys())}")
    raise KeyError(f"Unknown simulation type: Expect {tuple(map_dict.keys())}")


def check_palm_namelist_settings():
    """
    Check PALM namelist settings.
    """
    check_palm_grid_params()


def _find_optimal_npex_npey_with_core_num() -> tuple[int, int]:
    core_num = WRFRUN.config.get_core_num()
    sqrt_num = math.floor(math.sqrt(core_num))

    for _num in range(sqrt_num, 1, -1):
        if core_num % _num == 0:
            npex = core_num // _num
            npey = _num

            if npex / npey > 0.5:
                logger.error(
                    f"The optimal 'npex' and 'npey' is {(npex, npey)}, which differs extremely. Adjust your core num settings."
                )
                raise ValueError(
                    f"The optimal 'npex' and 'npey' is {(npex, npey)}, which differs extremely. Adjust your core num settings."
                )

            return (npex, npey)

    # We should never reach here, but an error still is raised here to eliminate linting error.
    logger.error(f"The optimal 'npex' and 'npey' is {(core_num, 1)}, which differs extremely. Adjust your core num settings.")
    raise ValueError(f"The optimal 'npex' and 'npey' is {(core_num, 1)}, which differs extremely. Adjust your core num settings.")


def check_palm_grid_params():
    """
    Check PALM grid parameters in the namelist.

    :raises ValueError: 'nx' and 'ny' not set in namelist.
    :raises NameError: 'nx', 'ny', 'npex' or 'npey' isn't integer.
    :raises ValueError: 'nx' and 'ny' 's value isn't right to work with other settings.
    """
    namelist_dict = WRFRUN.config.get_namelist("palm")
    initialization_parameters: dict = namelist_dict["initialization_parameters"]
    runtime_parameters: dict = namelist_dict["runtime_parameters"]

    point_num_x: int | None = initialization_parameters.get("nx")
    point_num_y: int | None = initialization_parameters.get("ny")
    npex: int | None = runtime_parameters.get("npex")
    npey: int | None = runtime_parameters.get("npey")

    if None in (point_num_x, point_num_y):
        logger.error("You MUST set 'nx' and 'ny' in PALM namelist.")
        raise ValueError("You MUST set 'nx' and 'ny' in PALM namelist.")

    if None in (npex, npey):
        logger.warning("Try to calculate optimal 'npex' and 'npey' with giving core nums.")
        npex, npey = _find_optimal_npex_npey_with_core_num()

    if not all(isinstance(x, int) for x in (point_num_x, point_num_y, npex, npey)):
        logger.error("(nx, ny, npex, npey) must all be integer. Check your namelist.")
        raise NameError("(nx, ny, npex, npey) must all be integer. Check your namelist.")

    # check psoler
    if initialization_parameters.get("psolver", "poisfft") == "multigrid":
        for value_x, value_y in zip([2, npex], [2, npey]):
            if (point_num_x + 1) % value_x != 0 or (point_num_y + 1) % value_y != 0:  # type: ignore
                logger.error(
                    (
                        "If you set 'psolver = multigrid', "
                        "then (nx+1) and (ny+1) must can be divided by 2 "
                        f"and corresponding assigned core number (here is {(npey, npey)}). "
                        "Adjust your namelist."
                    )
                )
                logger.error(
                    "Check: https://docs.palm-model.org/25.10.1/Reference/LES_Model/Namelists/#initialization_parameters--psolver"
                )
                raise ValueError("Check error logs above.")

    # check fft_method
    if initialization_parameters.get("fft_method", "temperton-algorithm") == "fftw":
        if (point_num_x + 1) % npex != 0 or (point_num_y + 1) % npey != 0:  # type: ignore
            logger.error(
                (
                    f"(nx+1) and (ny+1) must can be divided by corresponding assigned core number (here is {(npey, npey)}). "
                    "Adjust your namelist."
                )
            )
            raise ValueError(
                (
                    f"(nx+1) and (ny+1) must can be divided by corresponding assigned core number (here is {(npey, npey)}). "
                    "Adjust your namelist."
                )
            )

        if not (is_valid_palm_dimension(point_num_x + 1, npex) and is_valid_palm_dimension(point_num_y + 1, npey)):  # type: ignore
            best_nx = find_optimal_grid_number(point_num_x, npex)  # type: ignore
            best_ny = find_optimal_grid_number(point_num_y, npey)  # type: ignore

            logger.error(
                (
                    "If you set 'fft_method = fftw', "
                    "subgrid points number must can only be factorized by (2, 3, 5, 7), "
                    "with at most one additional factor of (11, 13). "
                    f"Change 'nx' and 'ny' in the namelist, best values we guess are: nx={best_nx}, ny={best_ny}, "
                    f"with npex={npex}, npey={npey}."
                )
            )
            logger.error(
                "Check: https://docs.palm-model.org/25.10.1/Reference/LES_Model/Namelists/#initialization_parameters--fft_method"
            )
            raise ValueError("Check error logs above.")


__all__ = ["prepare_palm_namelist", "get_namelist_save_name", "check_palm_namelist_settings", "check_palm_grid_params"]
