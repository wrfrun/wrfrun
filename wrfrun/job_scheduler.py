"""
wrfrun.job_scheduler
####################

``wrfrun`` provides functions to help users take care of the job scheduler.

.. autosummary::
    :toctree: generated/

    in_job_scheduler

How Does wrfrun Check If It Is In A Job Scheduler?
**************************************************

If you submit your task through ``wrfrun``, that is,
set ``submit_job = True`` in :class:`WRFRun <wrfrun.run.WRFRun>`,
an environment variable called ``WRFRUN_ENV_JOB_SCHEDULER`` will be set.
``wrfrun`` will determine if it is in a job scheduler by checking if ``WRFRUN_ENV_JOB_SCHEDULER`` appears in environment.

If you submit your task by your own,
it is recommended that add ``WRFRUN_ENV_JOB_SCHEDULER`` to the environment,
which can ensure ``wrfrun`` works properly in the job scheduler.
"""

__all__ = []
