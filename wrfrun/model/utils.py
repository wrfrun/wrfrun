"""
wrfrun.model.utils
##################

Utility functions used by models.

.. autosummary::
    :toctree: generated/

    clear_model_logs
"""

from ..core import WRFRUN
from .wrf.log import clear_wrf_logs


def clear_model_logs():
    """
    This function can automatically collect unsaved log files,
    and save them to the corresponding output directory of the ``Executable``.
    """
    WRFRUNConfig = WRFRUN.config

    func_map = {
        "wrf": clear_wrf_logs
    }

    for _model in func_map:
        if _model in WRFRUNConfig["model"] and WRFRUNConfig["model"][_model]["use"]:
            func_map[_model]()


__all__ = ["clear_model_logs"]
