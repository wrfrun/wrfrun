"""
wrfrun.core._constant
#####################

.. autosummary::
    :toctree: generated/

    ConstantMixIn

ConstantMixIn
*************

This class provides methods to manage runtime constants of ``wrfrun``.
"""

from os import environ
from os.path import abspath
from sys import platform

from ..log import logger
from .error import WRFRunContextError


class ConstantMixIn:
    """
    Define all variables that will be used by other components.
    """

    def __init__(self, work_dir: str, *args, **kwargs):
        """
        Define all variables that will be used by other components.

        These variables are related to ``wrfrun`` installation environments, configuration files and more.
        They are defined either directly or mapped using URIs to ensure consistent access across all components.

        :param work_dir: ``wrfrun`` work directory path.
        :type work_dir: str
        """
        # check system
        if platform != "linux":
            logger.debug("Not Linux system!")

        if work_dir != "" or platform != "linux":
            # set temporary dir path
            self._WRFRUN_TEMP_PATH = abspath(f"{work_dir}/tmp")
            self._WRFRUN_HOME_PATH = abspath(work_dir)

        else:
            # the path we may need to store temp files,
            # don't worry, it will be deleted once the system reboots
            self._WRFRUN_TEMP_PATH = "/tmp/wrfrun"
            user_home_path = f"{environ['HOME']}"

            # WRF may need a large disk space to store output, we can't run wrf in /tmp,
            # so we will create a folder in $HOME/.config to run wrf.
            # we need to check if we're running as a root user
            if user_home_path in ["/", "/root", ""]:
                logger.warning(
                    f"User's home path is '{user_home_path}', which means you are running this program as a root user"
                )
                logger.warning("It's not recommended to use wrfrun as a root user")
                logger.warning("Set user_home_path as /root")
                user_home_path = "/root"

            self._WRFRUN_HOME_PATH = f"{user_home_path}/.config/wrfrun"

        # workspace root path
        self._WRFRUN_WORKSPACE_ROOT = f"{self._WRFRUN_HOME_PATH}/workspace"
        self._WRFRUN_WORKSPACE_MODEL = f"{self._WRFRUN_WORKSPACE_ROOT}/model"
        self._WRFRUN_WORKSPACE_REPLAY = f"{self._WRFRUN_WORKSPACE_ROOT}/replay"

        # record WRF progress status
        self._WRFRUN_WORK_STATUS = ""

        # record context status
        self._WRFRUN_CONTEXT_STATUS = False

        self._WRFRUN_OUTPUT_PATH = ":WRFRUN_OUTPUT_PATH:"
        self._WRFRUN_RESOURCE_PATH = ":WRFRUN_RESOURCE_PATH:"

        self.IS_IN_REPLAY: bool = False

        self.IS_RECORDING: bool = False

        # in this mode, wrfrun will do all things except call the numerical model.
        # all output rules will also not be executed.
        self.FAKE_SIMULATION_MODE = False

        super().__init__(*args, **kwargs)

    def _get_uri_map(self) -> dict[str, str]:
        """
        Return URIs and their values.
        ``wrfrun`` will use this to register uri when initialize config.

        :return: A dict in which URIs are keys and their values are dictionary values.
        :rtype: dict
        """
        return {
            self.WRFRUN_TEMP_PATH: self._WRFRUN_TEMP_PATH,
            self.WRFRUN_HOME_PATH: self._WRFRUN_HOME_PATH,
            self.WRFRUN_WORKSPACE_ROOT: self._WRFRUN_WORKSPACE_ROOT,
            self.WRFRUN_WORKSPACE_MODEL: self._WRFRUN_WORKSPACE_MODEL,
            self.WRFRUN_WORKSPACE_REPLAY: self._WRFRUN_WORKSPACE_REPLAY,
        }

    @property
    def WRFRUN_WORKSPACE_REPLAY(self) -> str:
        """
        Path (URI) to store related files of ``wrfrun`` replay functionality.

        :return: URI.
        :rtype: str
        """
        return ":WRFRUN_WORKSPACE_REPLAY:"

    @property
    def WRFRUN_TEMP_PATH(self) -> str:
        """
        Path to store ``wrfrun`` temporary files.

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_TEMP_PATH:"

    @property
    def WRFRUN_HOME_PATH(self) -> str:
        """
        Root path of all others directories. .

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_HOME_PATH:"

    @property
    def WRFRUN_WORKSPACE_ROOT(self) -> str:
        """
        Path of the root workspace.

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_WORKSPACE_ROOT:"

    @property
    def WRFRUN_WORKSPACE_MODEL(self) -> str:
        """
        Path of the model workspace, in which ``wrfrun`` runs numerical models.

        :return: URI
        :rtype: str
        """
        return ":WRFRUN_WORKSPACE_MODEL:"

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

    @property
    def WRFRUN_OUTPUT_PATH(self) -> str:
        """
        The root path to store all outputs of the ``wrfrun`` and NWP model.

        :return: URI
        :rtype: str
        """
        return self._WRFRUN_OUTPUT_PATH

    @property
    def WRFRUN_RESOURCE_PATH(self) -> str:
        """
        The root path of all ``wrfrun`` resource files.

        :return: URI
        :rtype: str
        """
        return self._WRFRUN_RESOURCE_PATH

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
            logger.warning(
                "You are using wrfrun without entering `WRFRun` context, which may cause some functions don't work."
            )
            return self._WRFRUN_CONTEXT_STATUS

        logger.error("You need to enter `WRFRun` context to use wrfrun.")
        raise WRFRunContextError("You need to enter `WRFRun` context to use wrfrun.")

    def set_wrfrun_context(self, status: bool):
        """
        Change ``WRFRun`` context status to True or False.

        :param status: ``True`` or ``False``.
        :type status: bool
        """
        self._WRFRUN_CONTEXT_STATUS = status


__all__ = ["ConstantMixIn"]
