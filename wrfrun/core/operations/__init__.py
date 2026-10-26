"""
wrfrun.core.operations
######################

Project-level operations shared by command-line and agent interfaces.

.. autosummary::
    :toctree: generated/

    initialize_project
    add_models
    create_experiment
    ProfileInfo
    get_global_profile_path
    save_profile
    load_profile
    list_profiles
    remove_global_profile
    Job
    list_jobs
    get_job
    follow_job_log
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
