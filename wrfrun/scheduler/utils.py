"""
wrfrun.scheduler.utils
######################

Utility functions used by ``wrfrun`` scheduler part.

.. autosummary::
    :toctree: generated/

    get_core_num
"""

from wrfrun.core import WRFRUN_NEW


def get_core_num() -> int:
    """
    Get core number.

    :return: Core number.
    :rtype: int
    """
    return WRFRUN_NEW.config["core_num"]


__all__ = ["get_core_num"]
