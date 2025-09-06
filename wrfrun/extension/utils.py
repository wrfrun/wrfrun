"""
wrfrun.extension.utils
######################

Utility functions used by extensions.

.. autosummary::
    :toctree: generated/

    extension_postprocess
"""

from os import listdir
from os.path import exists
from shutil import copyfile
from typing import List, Optional

from wrfrun.core import WRFRUNConfig
from wrfrun.utils import check_path, logger


def extension_postprocess(output_dir: str, extension_id: str, outputs: Optional[List[str]] = None):
    """
    This function provides a unified postprocessing interface for all extensions.

    This function will save outputss and logs in ``output_dir`` to the ``{output_path}/extension_id`` and ``{output_path}/extension_id/logs``,
    in which ``output_path`` is defined in ``config.toml``.
    Files end with ``.log`` are treated as log files, while others are treated as outputs.
    You can save specific outputs by giving their names through the argument ``outputs``.

    :param output_dir: Absolute path of output directory.
    :type output_dir: str
    :param extension_id: A unique id to distinguish different extensions.
                         Outputs and logs will be saved to ``{output_path}/extension_id`` and ``{output_path}/extension_id/logs``,
                         in which``output_path`` is defined in ``config.toml``.
    :type extension_id: str
    :param outputs: A list contains multiple filenames. Files in this will be treated as outputs.
    :type outputs: list
    """
    output_path = WRFRUNConfig.WRFRUN_OUTPUT_PATH
    output_save_path = f"{output_path}/{extension_id}"
    log_save_path = f"{output_path}/{extension_id}/logs"

    output_save_path = WRFRUNConfig.parse_resource_uri(output_save_path)
    log_save_path = WRFRUNConfig.parse_resource_uri(log_save_path)
    output_dir = WRFRUNConfig.parse_resource_uri(output_dir)

    filenames = listdir(output_dir)
    logs = [x for x in filenames if x.endswith(".log")]
    if outputs is None:
        outputs = list(set(filenames) - set(logs))

    check_path(output_save_path, log_save_path)

    logger.info(f"Saving outputs and logs to {output_save_path}")

    for _file in outputs:
        if exists(f"{output_dir}/{_file}"):
            copyfile(f"{output_dir}/{_file}", f"{output_save_path}/{_file}")
        else:
            logger.warning(f"Output {_file} not found")

    for _log in logs:
        copyfile(f"{output_dir}/{_log}", f"{log_save_path}/{_log}")


__all__ = ["extension_postprocess"]
