"""
Conditional executable inputs for ARPS.

.. autosummary::
    :toctree: generated/

    InputRequirement
    stage_input_requirements
"""

from dataclasses import dataclass
from typing import Callable, Sequence

from wrfrun.core import ExecutableBase


@dataclass(frozen=True)
class InputRequirement:
    """Describe one optional executable input."""

    name: str
    enabled: Callable[[ExecutableBase, dict], bool]
    stage: Callable[[ExecutableBase, dict], None]


def stage_input_requirements(executable: ExecutableBase, namelist: dict, requirements: Sequence[InputRequirement]) -> None:
    """Stage every input enabled by the current namelist."""
    for requirement in requirements:
        if requirement.enabled(executable, namelist):
            requirement.stage(executable, namelist)


__all__ = ["InputRequirement", "stage_input_requirements"]
