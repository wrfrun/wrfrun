"""
Conditional executable inputs for ARPS.

.. autosummary::
    :toctree: generated/

    InputRequirement
    stage_input_requirements
"""

import logging
from dataclasses import dataclass
from typing import Callable, Sequence

from wrfrun.core import ExecutableBase

LOGGER = logging.getLogger("wrfrun")


@dataclass(frozen=True)
class IORequirement:
    """Describe one optional executable input."""

    name: str
    enabled: Callable[[ExecutableBase, dict], bool]
    stage: Callable[[ExecutableBase, dict], None]


def stage_io_requirements(executable: ExecutableBase, namelist: dict, requirements: Sequence[IORequirement]) -> None:
    """Stage every input/output enabled by the current namelist."""
    LOGGER.debug(f"Stage IO files for {executable.name}")
    LOGGER.debug("Got namelist: ")
    LOGGER.debug(namelist)
    LOGGER.debug("Got requirements: ")
    LOGGER.debug(requirements)

    for requirement in requirements:
        if requirement.enabled(executable, namelist):
            requirement.stage(executable, namelist)


__all__ = ["IORequirement", "stage_io_requirements"]
