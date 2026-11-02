"""
wrfrun.cli
##########

Command-line interface for project, experiment, profile, and job operations.

Submodules
**********

=============================================== ======================================================
:doc:`main </api/cli.main>`                     Argument parser and ``wrfrun`` command entry point.
:doc:`project </api/cli.project>`               Project initialization and model-management handlers.
:doc:`experiment </api/cli.experiment>`         Experiment-creation command handler.
:doc:`profile </api/cli.profile>`               Reusable configuration-profile command handlers.
:doc:`jobs </api/cli.jobs>`                     Run-status listing and log-following command handler.
=============================================== ======================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    main <cli.main>
    project <cli.project>
    experiment <cli.experiment>
    profile <cli.profile>
    jobs <cli.jobs>
"""

from .main import main_entry

__all__ = ["main_entry"]
