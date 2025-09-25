"""
wrfrun.scheduler.env
####################

Functions to manage environment variables in job scheduler.

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

from os import environ


def in_job_scheduler() -> bool:
    """
    Check if ``wrfrun`` runs in a job scheduler task.

    This function checks the environment variable ``WRFRUN_ENV_JOB_SCHEDULER``
    to determine if ``wrfrun`` is running in a job scheduler task.

    :return: ``True`` if in a job scheduler task, else ``False``.
    :rtype: bool
    """
    if "WRFRUN_ENV_JOB_SCHEDULER" in environ:
        return True
    else:
        return False


__all__ = ["in_job_scheduler"]
