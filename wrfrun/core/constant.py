"""
Initiate constant variables for wrf running
"""

from os import environ

from wrfrun.utils import logger


class _Constants:
    def __init__(self):
        # the path we may need to store temp file,
        # don't worry, it will be deleted once the system reboots
        self.WRFRUN_TEMP_PATH = "/tmp/wrfrun"
        # because WRF may need a large disk space to store output, we can't run wrf in /tmp,
        # so we will create a folder in $HOME/.config to run wrf.
        # but we need to check if we're running as a root user
        USER_HOME_PATH = f"{environ['HOME']}"
        # check user's home path
        if USER_HOME_PATH in ["/", "/root", ""]:
            logger.warning(
                f"User's home path is \"{USER_HOME_PATH}\", which means you are running this program as a root user")
            logger.warning("It's not recommended to use wrfrun as a root user")
            logger.warning(f"Set USER_HOME_PATH as /root")
            USER_HOME_PATH = "/root"

        self.USER_WRF_HOME_PATH = f"{USER_HOME_PATH}/.config/wrfrun"

        # work path to run WPS, WRF and WRFDA
        self.WORK_PATH = f"{self.USER_WRF_HOME_PATH}/workspace"
        self.WPS_WORK_PATH = f"{self.WORK_PATH}/WPS"
        self.WRF_WORK_PATH = f"{self.WORK_PATH}/WRF"
        self.WRFDA_WORK_PATH = f"{self.WORK_PATH}/WRFDA"

        # record WRF progress status
        self.WRF_STATUS = ""

        # global variable to record context status
        self.WRFRUN_CONTEXT_STATUS = False

        # WRFDA is not necessary
        self.USE_WRFDA: bool = False

        self._user_config = {}

    def get_temp_path(self):
        """
        Return the value of ``WRFRUN_TEMP_PATH``.

        :return:
        :rtype:
        """
        return self.WRFRUN_TEMP_PATH

    def get_workspace_path(self):
        return self.WORK_PATH

    def get_work_path(self, name: str):
        """
        Get the work path.

        Args:
            name: ``"wps"``, ``"wrf"``, or ``"wrfda"``.

        Returns:
            Work path of ``name``.

        """
        if name == "wrf":
            return self.WRF_WORK_PATH
        elif name == "wps":
            return self.WPS_WORK_PATH
        elif name == "wrfda":
            return self.WRFDA_WORK_PATH
        else:
            raise KeyError(f"name should be 'wps', 'wrf' or 'wrfda', but is '{name}'")

    def get_wrf_status(self):
        return self.WRF_STATUS

    def set_wrf_status(self, status: str):
        self.WRF_STATUS = status

    def check_wrfrun_context(self, error=False):
        """Check we're in WRFRun context or not

            Args:
                error (bool, optional): Raise an error if `error=True` when we are not in WRFRun context.

            Returns:
                bool: True if we're in, False if we are not.
            """
        if not self.WRFRUN_CONTEXT_STATUS:

            if error:
                # print error message and raise an error
                logger.error(
                    f"You need to be in WRFRun context to run following code. Enter context with code: `with WRFRun(config):`"
                )
                raise RuntimeError(f"You need to be in WRFRun context to run following code. Enter context with code: `with WRFRun(config):`")

            else:
                logger.warning(
                    f"You are running following code without entering WRFRun context, which may cause some functions don't work. Take care."
                )

        return self.WRFRUN_CONTEXT_STATUS

    def set_wrfrun_context(self, status: bool):
        """Change WRFRun context to True or False

        Args:
            status (bool): True or False.
        """
        self.WRFRUN_CONTEXT_STATUS = status


WRFRUNConstants = _Constants()


__all__ = ["WRFRUNConstants"]
