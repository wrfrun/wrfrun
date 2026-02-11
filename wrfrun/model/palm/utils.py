"""
wrfrun.model.palm.utils
#######################

.. autosummary::
    :toctree: generated/

    get_input_subfix

Utility functions used by ``wrfrun.model.palm``.
"""

import re

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


__all__ = ["get_input_postfix"]
