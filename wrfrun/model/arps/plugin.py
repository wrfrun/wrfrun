"""
wrfrun.model.arps.plugin
########################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging

from wrfrun.core import WRFRUN_NEW, ExecRegisterError

from .arpstrn import ARPSTrn
from .core import ARPS, ARPSSFC, EXT2ARPS
from .workspace import check_arps_workspace, prepare_arps_workspace

LOGGER = logging.getLogger("wrfrun")


def register_exec(name: str, cls: type):
    """
    Check and register the ``Executable``.
    """
    if WRFRUN_NEW.registry.is_registered(name):
        LOGGER.error(f"'{name}' is already registered. DO NOT register [magenta]Executable[/magenta] repeatedly.")
        raise ExecRegisterError(f"'{name}' is already registered. DO NOT register Executable repeatedly.")

    WRFRUN_NEW.registry.register_exec(name, cls)


class ARPSPlugin:
    """
    ARPS model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "arps"

    def register(self):
        """
        Register ARPS ``Executable``.
        """
        register_exec("arpssfc", ARPSSFC)
        register_exec("arpstrn", ARPSTrn)
        register_exec("ext2arps", EXT2ARPS)
        register_exec("arps", ARPS)

        WRFRUN_NEW.workspace.register_init_func("arps", prepare_arps_workspace)
        WRFRUN_NEW.workspace.register_check_func("arps", check_arps_workspace)

        WRFRUN_NEW.resource.register_provider("workspace_arps", WRFRUN_NEW.resource.WRFRUN_WORKSPACE_ROOT / "arps")


__all__ = ["ARPSPlugin"]
