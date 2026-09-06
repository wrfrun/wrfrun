"""
wrfrun.model.palm.plugin
########################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging

from wrfrun.core import WRFRUN_NEW

from .core import ROMS

LOGGER = logging.getLogger("wrfrun")


class ROMSPlugin:
    """
    ROMS model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "roms"

    def register(self):
        """
        Register ROMS ``Executable``.
        """
        WRFRUN_NEW.registry.register_exec("roms", ROMS)

        WRFRUN_NEW.resource.register_provider("workspace_roms", WRFRUN_NEW.resource.WRFRUN_WORKSPACE_ROOT / "roms")


__all__ = ["ROMSPlugin"]
