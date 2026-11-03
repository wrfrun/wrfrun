"""
wrfrun.model.palm
#################

PALM model integration.

Submodules
**********

====================================================================== ========================================================
:doc:`config </api/model.palm.config>`                                     PALM configuration-file processing.
:doc:`core </api/model.palm.core>`                                         PALM executable and wrapper.
:doc:`namelist </api/model.palm.namelist>`                                 PALM namelist preparation and validation.
:doc:`plugin </api/model.palm.plugin>`                                     PALM plugin registration.
:doc:`utils </api/model.palm.utils>`                                       PALM utility functions.
:doc:`workspace </api/model.palm.workspace>`                               PALM workspace preparation and validation.
====================================================================== ========================================================

``wrfrun`` runs PALM through its ``palmrun`` script.

.. toctree::
    :maxdepth: 1
    :hidden:

    config <model.palm.config>
    core <model.palm.core>
    namelist <model.palm.namelist>
    plugin <model.palm.plugin>
    utils <model.palm.utils>
    workspace <model.palm.workspace>
"""

from .config import parse_palm_config, prepare_palm_config, read_palm_config, write_palm_config
from .core import PALMRun, palmrun
from .namelist import (
    check_palm_grid_params,
    check_palm_namelist_settings,
    get_namelist_save_name,
    prepare_palm_namelist,
)
from .utils import find_optimal_grid_number, get_input_postfix, is_valid_palm_dimension

__all__ = [
    "PALMRun",
    "check_palm_grid_params",
    "check_palm_namelist_settings",
    "find_optimal_grid_number",
    "get_input_postfix",
    "get_namelist_save_name",
    "is_valid_palm_dimension",
    "palmrun",
    "parse_palm_config",
    "prepare_palm_config",
    "prepare_palm_namelist",
    "read_palm_config",
    "write_palm_config",
]
