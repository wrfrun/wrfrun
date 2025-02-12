from os import listdir
from os.path import exists
from shutil import copyfile
from typing import List, Optional

from wrfrun.core import WRFRUNConfig
from wrfrun.utils import check_path, logger


def extension_postprocess(output_dir: str, extension_id: str, outputs: Optional[List[str]] = None):
    """
    Apply postprocess after running an extension.
    This function can help you save all files and logs in ``output_dir`` to the ``output_path/extension_id`` and ``output_path/extension_id/logs``,
    ``output_path`` is defined in ``config.yaml``.
    Files end with ``.log`` are treated as log files, while others are treated as outputs.
    You can specify outputs by giving their names through parameter ``outputs``.

    Save all outputs of ungrib.

    >>> from wrfrun.extension.utils import extension_postprocess
    >>> output_dir_path = "/WPS/outputs"
    >>> extension_postprocess(output_dir_path, "ungrib")

    Save outputs start with ``SST_FILE`` of ungrib.

    >>> from os import listdir
    >>> from wrfrun.extension.utils import extension_postprocess
    >>> output_dir_path = "/WPS/outputs"
    >>> outputs_name = [x for x in listdir(output_dir_path) if x.startswith("SST_FILE")]    # type: ignore
    >>> extension_postprocess(output_dir_path, "ungrib", outputs=outputs_name)

    :param output_dir: Absolute path of output directory.
    :param extension_id: A unique id to distinguish different extensions.
                         And all files and logs will be saved to ``output_path/extension_id`` and ``output_path/extension_id/logs``,
                         ``output_path`` is defined in ``config.yaml``.
    :param outputs: A list contains multiple filenames. Files in this will be treated as outputs.
    :return:
    """
    filenames = listdir(output_dir)
    logs = [x for x in filenames if x.endswith(".log")]
    if outputs is None:
        outputs = list(set(filenames) - set(logs))

    output_path = WRFRUNConfig.get_output_path()
    output_save_path = f"{output_path}/{extension_id}"
    log_save_path = f"{output_path}/{extension_id}/logs"
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
