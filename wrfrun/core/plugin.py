"""
wrfrun.core.plugin
##################

``wrfrun`` uses the plugin class to find and register models and extensions.

.. autosummary::
    :toctree: generated/

    PluginProtocol
"""

from typing import Protocol

from .runtime.registry import ExecutableRegistry


class PluginProtocol(Protocol):
    """
    Plugin protocol for model and extension.
    """

    name: str

    def register(self, registry: ExecutableRegistry):
        """
        Method which registers information to the registry.
        """
        ...


__all__ = ["PluginProtocol"]
