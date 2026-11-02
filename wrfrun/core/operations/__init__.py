"""
wrfrun.core.operations
######################

Project-level operations shared by command-line and agent interfaces.

Submodules
**********

===================================================== ======================================================================
:doc:`project </api/core.operations.project>`         Project initialization and model-management operations.
:doc:`experiment </api/core.operations.experiment>`   Experiment creation and input staging operations.
:doc:`profile </api/core.operations.profile>`         Reusable configuration-profile operations.
:doc:`jobs </api/core.operations.jobs>`               Run-status inspection and log-following operations.
===================================================== ======================================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    project <core.operations.project>
    experiment <core.operations.experiment>
    profile <core.operations.profile>
    jobs <core.operations.jobs>
"""

from .experiment import create_experiment
from .jobs import Job, follow_job_log, get_job, list_jobs
from .profile import ProfileInfo, get_global_profile_path, list_profiles, load_profile, remove_global_profile, save_profile
from .project import add_models, initialize_project

__all__ = [
    "Job",
    "ProfileInfo",
    "add_models",
    "create_experiment",
    "follow_job_log",
    "get_global_profile_path",
    "get_job",
    "initialize_project",
    "list_jobs",
    "list_profiles",
    "load_profile",
    "remove_global_profile",
    "save_profile",
]
