"""
wrfrun.model.palm.plugin
########################

Define plugin class which will be provided to ``wrfrun`` to register ``Executable``.
"""

import logging
from pathlib import Path

from wrfrun.core import WRFRUN_NEW

from .core import PALMRun
from .workspace import check_palm_workspace, prepare_palm_workspace

LOGGER = logging.getLogger("wrfrun")


class PALMPlugin:
    """
    PALM model plugin.

    For information about plugin please check :class:`PluginProtocol<wrfrun.core.plugin.PluginProtocol>`,
    """

    name = "palm"

    def initialize_project_files(self, project_path: Path):
        """Create PALM namelist directories in a project."""
        (project_path / "configs/namelists/templates/palm/palm").mkdir(parents=True, exist_ok=True)
        (project_path / "configs/namelists/user/palm/palm").mkdir(parents=True, exist_ok=True)

    def initialize_experiment_files(self, experiment_path: Path):
        """Create PALM namelist directories for one experiment."""
        (experiment_path / "namelists/palm/palm").mkdir(parents=True, exist_ok=True)

    def register(self):
        """
        Register PALM ``Executable``.
        """
        WRFRUN_NEW.registry.register_exec("palmrun", PALMRun)

        WRFRUN_NEW.resource.register_provider("workspace_palm", WRFRUN_NEW.resource.WORKSPACE_DIR / "palm")

        WRFRUN_NEW.workspace.register_init_func("palm", prepare_palm_workspace)
        WRFRUN_NEW.workspace.register_check_func("palm", check_palm_workspace)


__all__ = ["PALMPlugin"]
