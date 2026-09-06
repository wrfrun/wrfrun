"""
wrfrun.model.palm.plugin
########################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging

from wrfrun.core import WRFRUN_NEW

from .core import PALMRun

LOGGER = logging.getLogger("wrfrun")


class PALMPlugin:
    """
    PALM model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "palm"

    def register(self):
        """
        Register PALM ``Executable``.
        """
        WRFRUN_NEW.registry.register_exec("palmrun", PALMRun)

        WRFRUN_NEW.resource.register_provider("workspace_palm", WRFRUN_NEW.resource.WRFRUN_WORKSPACE_ROOT / "palm")


__all__ = ["PALMPlugin"]
