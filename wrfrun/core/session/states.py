"""
wrfrun.core.session.states
##########################

``wrfrun`` session states store.

.. autosummary::
    :toctree: generated/

    WRFRunStates
"""

import logging

from ..error import WRFRunContextError
from ._debug import DebugMixIn

LOGGER = logging.getLogger("wrfrun")


class WRFRunStates(DebugMixIn):
    """
    ``wrfrun`` session states store.
    """

    def __init__(self):
        """
        ``wrfrun`` session states store.
        """
        super().__init__()

        # record context status
        self._WRFRUN_CONTEXT_STATUS = False
        # record WRF progress status
        self._WRFRUN_WORK_STATUS = ""

        self.IS_IN_REPLAY: bool = False
        self.IS_RECORDING: bool = False

        # in this mode, wrfrun will do all things except call the numerical model.
        # all output rules will also not be executed.
        self.FAKE_SIMULATION_MODE = False

    def check_wrfrun_context(self, error=False) -> bool:
        """
        Check if in WRFRun context or not.

        :param error: An exception :class:`WRFRunContextError` will be raised
                      if ``error==True`` when we are not in WRFRun context.
        :type error: bool
        :return: True or False.
        :rtype: bool
        """
        if self._WRFRUN_CONTEXT_STATUS:
            return self._WRFRUN_CONTEXT_STATUS

        if not error:
            LOGGER.warning("You are using wrfrun without entering `WRFRun` context, which may cause some functions don't work.")
            return self._WRFRUN_CONTEXT_STATUS

        LOGGER.error("You need to enter `WRFRun` context to use wrfrun.")
        raise WRFRunContextError("You need to enter `WRFRun` context to use wrfrun.")

    def set_wrfrun_context(self, status: bool):
        """
        Change ``WRFRun`` context status to True or False.

        :param status: ``True`` or ``False``.
        :type status: bool
        """
        self._WRFRUN_CONTEXT_STATUS = status

    @property
    def WRFRUN_WORK_STATUS(self) -> str:
        """
        ``wrfrun`` work status.

        This attribute can be changed by ``Executable`` to reflect the current work progress of ``wrfrun``.
        The returned string is the name of ``Executable``.

        :return: A string reflect the current work progress.
        :rtype: str
        """
        return self._WRFRUN_WORK_STATUS

    @WRFRUN_WORK_STATUS.setter
    def WRFRUN_WORK_STATUS(self, value: str):
        """
        Set ``wrfrun`` work status.

        ``wrfrun`` recommends ``Executable`` set the status string with their name,
        so to avoid the possible conflicts with other ``Executable``,
        and the user can easily understand the current work progress.

        :param value: A string represents the work status.
        :type value: str
        """
        self._WRFRUN_WORK_STATUS = value


__all__ = ["WRFRunStates"]
