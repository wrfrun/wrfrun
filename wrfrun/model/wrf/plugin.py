"""
wrfrun.model.wrf.plugin
#######################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging

from wrfrun.core.error import ExecRegisterError
from wrfrun.core.runtime.registry import ExecutableRegistry

from .core import DFI, WRF, GeoGrid, MetGrid, NDown, Real, UnGrib

LOGGER = logging.getLogger("wrfrun")


def register_exec(registry: ExecutableRegistry, name: str, cls: type):
    """
    Check and register the ``Executable``.
    """
    if registry.is_registered(name):
        LOGGER.error(f"'{name}' is already registered. DO NOT register [magenta]Executable[/magenta] repeatedly.")
        raise ExecRegisterError(f"'{name}' is already registered. DO NOT register Executable repeatedly.")

    registry.register_exec(name, cls)


class WRFPlugin:
    """
    WRF model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "wrf"

    def register(self, registry: ExecutableRegistry):
        """
        Register WRF ``Executable``.
        """
        register_exec(registry, "geogrid", GeoGrid)
        register_exec(registry, "ungrib", UnGrib)
        register_exec(registry, "metgrid", MetGrid)
        register_exec(registry, "real", Real)
        register_exec(registry, "wrf", WRF)
        register_exec(registry, "dfi", DFI)
        register_exec(registry, "ndown", NDown)


__all__ = ["WRFPlugin"]
