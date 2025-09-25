"""
wrfrun.scheduler
################

``wrfrun`` provides functions to help users take care of the job scheduler.

Submodules
**********

======================================= ===========================================================
:doc:`env </api/scheduler.env>`         Functions to manage environment variables in job scheduler.
:doc:`lsf </api/scheduler.lsf>`         Scheduler interface for LSF job scheduler.
:doc:`pbs </api/scheduler.pbs>`         Scheduler interface for PBS job scheduler.
:doc:`script </api/scheduler.script>`   Generate shell scripts for job scheduler.
:doc:`slurm </api/scheduler.slurm>`     Scheduler interface for Slurm job scheduler.
:doc:`utils </api/scheduler.utils>`     Utility functions.
======================================= ===========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    env <scheduler.env>
    lsf <scheduler.lsf>
    pbs <scheduler.pbs>
    slurm <scheduler.slurm>
    utils <scheduler.utils>
"""

from .env import *
from .lsf import *
from .pbs import *
from .script import *
from .slurm import *
from .utils import *
