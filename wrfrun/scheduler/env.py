"""
wrfrun.scheduler.env
####################

Detect execution within a scheduler task.

.. autosummary::
    :toctree: generated/

    in_job_scheduler

Scheduler Environment
*********************

Scripts produced by :func:`~wrfrun.scheduler.core.prepare_scheduler_script`
export ``WRFRUN_ENV_JOB_SCHEDULER=1``. :func:`in_job_scheduler` uses the
presence of that variable to identify scheduler execution. A manually managed
script can export the same variable when it needs the same behavior.
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
