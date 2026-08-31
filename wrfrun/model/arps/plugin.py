"""
wrfrun.model.arps.plugin
########################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging

from wrfrun.core.error import ExecRegisterError
from wrfrun.core.runtime.registry import ExecutableRegistry

from .arpstrn import ARPSTrn
from .core import ARPS, ARPSSFC, EXT2ARPS

LOGGER = logging.getLogger("wrfrun")


def register_exec(registry: ExecutableRegistry, name: str, cls: type):
    """
    Check and register the ``Executable``.
    """
    if registry.is_registered(name):
        LOGGER.error(f"'{name}' is already registered. DO NOT register [magenta]Executable[/magenta] repeatedly.")
        raise ExecRegisterError(f"'{name}' is already registered. DO NOT register Executable repeatedly.")

    registry.register_exec(name, cls)


class ARPSPlugin:
    """
    ARPS model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "arps"

    def register(self, registry: ExecutableRegistry):
        """
        Register ARPS ``Executable``.
        """
        register_exec(registry, "arpssfc", ARPSSFC)
        register_exec(registry, "arpstrn", ARPSTrn)
        register_exec(registry, "ext2arps", EXT2ARPS)
        register_exec(registry, "arps", ARPS)


__all__ = ["ARPSPlugin"]
