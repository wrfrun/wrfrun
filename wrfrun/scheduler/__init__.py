"""
wrfrun.scheduler
################

Prepare scheduler submission scripts and identify scheduler jobs.

Submodules
**********

======================================= ========================================================
:doc:`backend </api/scheduler.backend>` Scheduler-backend protocol and lookup.
:doc:`core </api/scheduler.core>`       Submission-script creation and job submission.
:doc:`env </api/scheduler.env>`         Scheduler-environment detection.
:doc:`lsf </api/scheduler.lsf>`         LSF backend and script settings.
:doc:`pbs </api/scheduler.pbs>`         PBS backend and script settings.
:doc:`slurm </api/scheduler.slurm>`     Slurm backend and script settings.
:doc:`utils </api/scheduler.utils>`     Shared scheduler utilities.
======================================= ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    backend <scheduler.backend>
    core <scheduler.core>
    env <scheduler.env>
    lsf <scheduler.lsf>
    pbs <scheduler.pbs>
    slurm <scheduler.slurm>
    utils <scheduler.utils>
"""

from .backend import SchedulerBackend, get_scheduler_backend
from .core import detect_scheduler_job, prepare_scheduler_script, submit_scheduler_task
from .env import in_job_scheduler
from .lsf import LSFBackend, lsf_generate_settings
from .pbs import PBSBackend, pbs_generate_settings
from .slurm import SlurmBackend, slurm_generate_settings
from .utils import get_core_num

__all__ = [
    "LSFBackend",
    "PBSBackend",
    "SchedulerBackend",
    "SlurmBackend",
    "detect_scheduler_job",
    "get_core_num",
    "get_scheduler_backend",
    "in_job_scheduler",
    "lsf_generate_settings",
    "pbs_generate_settings",
    "prepare_scheduler_script",
    "slurm_generate_settings",
    "submit_scheduler_task",
]
