"""
wrfrun.scheduler.utils
######################

Shared scheduler utilities.

.. autosummary::
    :toctree: generated/

    get_core_num
"""

from wrfrun.core import WRFRUN


def get_core_num() -> int:
    """
    Return the configured number of cores.

    :return: Core number.
    :rtype: int
    """
    return WRFRUN.config["core_num"]


__all__ = ["get_core_num"]
