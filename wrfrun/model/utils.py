"""
wrfrun.model.utils
##################

Utilities shared by enabled model integrations.

.. autosummary::
    :toctree: generated/

    clear_model_logs
"""

from ..core import WRFRUN


def clear_model_logs():
    """Collect unsaved WRF logs when WRF is enabled."""
    config = WRFRUN.config

    if "wrf" in config["model"] and config["model"]["wrf"]["use"]:
        from .wrf.log import clear_wrf_logs

        clear_wrf_logs()


__all__ = ["clear_model_logs"]
