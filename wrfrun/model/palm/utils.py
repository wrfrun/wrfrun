"""
wrfrun.model.palm.utils
#######################

.. autosummary::
    :toctree: generated/

    get_input_postfix

Utility functions used by ``wrfrun.model.palm``.
"""

import logging
import re

LOGGER = logging.getLogger("wrfrun")

# Get from PALM file ".palm.iofile"
PALM_INPUT_SUBFIX = [
    "_p3d",
    "_p3dr",
    "_pcr",
    "_nav",
    "_topo",
    "_prtids",
    "_canopy",
    "_nudge",
    "_lsf",
    "_wtm",
    "_stg",
    "_static",
    "_dynamic",
    "_salsa",
    "_chemistry",
    "_dcep",
    "_slurb",
    "_emis_generic",
    "_emis_domestic",
    "_emis_nonstat",
    "_emis_traffic",
    "_traffic",
    "_uv",
    "_vmeas",
    "_wtmpar",
    "_rlw",
    "_rsw",
    "_ts_options",
    "_ts_back_atm",
    "_d3d",
    "_rprt",
    "_spinup",
    "_svf",
]


def get_input_postfix(filename: str) -> str:
    """
    Parse the file name and get it PALM postfix string.

    :param filename: Input file name.
    :type filename: str
    :return: PALM postfix string.
    :rtype: str
    """
    res = re.search("(" + "|".join(PALM_INPUT_SUBFIX) + ")$", filename)

    if res:
        return res.group(0)

    else:
        return ""


def is_valid_palm_dimension(point_number: int, core_num: int = 1) -> bool:
    """
    Check whether a PALM horizontal dimension is valid.

    A valid value must be divisible by ``divisor`` first. After dividing by
    ``divisor``, the quotient can only be factorized by ``2``, ``3``, ``5``,
    and ``7``, with at most one additional factor of ``11`` or ``13``.

    :param point_number: Horizontal dimension to validate, usually ``nx + 1`` or ``ny + 1``.
    :type point_number: int
    :param core_num: The number of MPI processes assigned to one horizontal direction.
                     Defaults to ``1``.
    :type core_num: int
    :return: True if the dimension satisfies PALM's constraint, otherwise False.
    :rtype: bool
    """
    if point_number <= 0 or core_num <= 0:
        LOGGER.error("Number of point and CPU core must be a positive number.")
        raise ValueError("Number of point and CPU core must be a positive number.")

    if point_number % core_num != 0:
        return False

    remainder = point_number // core_num
    for factor in (2, 3, 5, 7):
        while remainder % factor == 0:
            remainder //= factor

    return remainder in (1, 11, 13)


def find_optimal_grid_number(min_value: int, core_num: int = 1) -> int:
    """
    Find the best grid number for PALM grid.

    :param min_value: Minimum grid number.
    :type min_value: int
    :param core_num: The number of MPI processes assigned to one horizontal direction.
                     Defaults to ``1``.
    :type core_num: int
    :return: Best grid number.
    :rtype: int
    """
    grid_number = max(1, min_value)
    while not is_valid_palm_dimension(grid_number + 1, core_num):
        grid_number += 1

    return grid_number


__all__ = ["get_input_postfix", "is_valid_palm_dimension", "find_optimal_grid_number"]
