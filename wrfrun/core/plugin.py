"""
wrfrun.core.plugin
##################

``wrfrun`` uses the plugin class to find and register models and extensions.

.. autosummary::
    :toctree: generated/

    PluginProtocol
"""

from pathlib import Path
from typing import Protocol


class PluginProtocol(Protocol):
    """
    Plugin protocol for model and extension.
    """

    name: str

    def register(self):
        """
        Method which registers information to the registry.
        """
        ...

    def initialize_project_files(self, project_path: Path):
        """Create model-owned project files and directories."""
        ...


__all__ = ["PluginProtocol"]
