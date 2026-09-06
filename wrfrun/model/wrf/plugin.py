"""
wrfrun.model.wrf.plugin
#######################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging

from wrfrun.core import WRFRUN_NEW, ExecRegisterError

from .core import DFI, WRF, GeoGrid, MetGrid, NDown, Real, UnGrib
from .workspace import check_wrf_workspace, prepare_wrf_workspace

LOGGER = logging.getLogger("wrfrun")


def register_exec(name: str, cls: type):
    """
    Check and register the ``Executable``.
    """
    if WRFRUN_NEW.registry.is_registered(name):
        LOGGER.error(f"'{name}' is already registered. DO NOT register [magenta]Executable[/magenta] repeatedly.")
        raise ExecRegisterError(f"'{name}' is already registered. DO NOT register Executable repeatedly.")

    WRFRUN_NEW.registry.register_exec(name, cls)


class WRFPlugin:
    """
    WRF model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "wrf"

    def register(self):
        """
        Register WRF ``Executable``.
        """
        register_exec("geogrid", GeoGrid)
        register_exec("ungrib", UnGrib)
        register_exec("metgrid", MetGrid)
        register_exec("real", Real)
        register_exec("wrf", WRF)
        register_exec("dfi", DFI)
        register_exec("ndown", NDown)

        WRFRUN_NEW.workspace.register_init_func("wrf", prepare_wrf_workspace)
        WRFRUN_NEW.workspace.register_check_func("wrf", check_wrf_workspace)

        WRFRUN_NEW.resource.register_provider("workspace_wrf", WRFRUN_NEW.resource.WRFRUN_WORKSPACE_ROOT / "wrf")


__all__ = ["WRFPlugin"]
