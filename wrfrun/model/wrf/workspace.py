from os import listdir, makedirs, symlink
from os.path import exists

from wrfrun import WRFRUNConfig
from wrfrun.utils import logger

_BASE_WORKSPACE = f"{WRFRUNConfig.WRFRUN_WORKSPACE_ROOT}/wrf"
MODEL_WPS_WORKSPACE = f"{_BASE_WORKSPACE}/WPS"
MODEL_WRF_WORKSPACE = f"{_BASE_WORKSPACE}/WRF"
MODEL_WRFDA_WORKSPACE = f"{_BASE_WORKSPACE}/WRFDA"


def wrf_prepare_workspace() -> bool:
    """
    Initialize workspace for WPS / WRF model.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    logger.info("Initializing workspace for WPS/WRF model.")

    if not exists(model_workspace_path):
        logger.warning(f"Root workspace path {model_workspace_path} does not exist.")
        logger.warning(f"Please call `prepare_workspace()` to re-initialize your whole workspace.")
        return False


