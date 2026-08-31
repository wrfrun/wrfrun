"""
wrfrun.core.states.states
#########################

State store port.

.. autosummary::
    :toctree: generated/


"""

from dataclasses import dataclass

from .config import ConfigService
from .namelist import NamelistService
from .states import WRFRunStates


@dataclass(frozen=True)
class StatesService:
    """
    State service.
    """

    config: ConfigService
    """
    ``wrfrun`` config store.
    """

    namelist: NamelistService
    """
    Namelist store.
    """

    states: WRFRunStates
    """
    Runtime states store.
    """


__all__ = ["StatesService"]
