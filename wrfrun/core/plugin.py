"""
wrfrun.core.plugin
##################

``wrfrun`` uses the plugin class to find and register models and extensions.

.. autosummary::
    :toctree: generated/

    PluginProtocol
"""

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


__all__ = ["PluginProtocol"]
