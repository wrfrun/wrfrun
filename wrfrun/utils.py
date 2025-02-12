import logging
import subprocess
from datetime import datetime
from os import chdir, getcwd, makedirs
from os.path import exists
from shutil import rmtree
from time import time
from typing import Optional

from rich.logging import RichHandler

# init a logger
logger = logging.getLogger("wrfrun")
formatter = logging.Formatter(
    "%(name)s :: %(message)s", datefmt="%m-%d %H:%M:%S")
# use rich handler
handler = RichHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

LOG_LEVEL = {
    "cdsapi": logging.INFO,
    "cfgrib": logging.ERROR,
}

# change useful logger handler
for logger_name in ["cdsapi", "cfgrib"]:
    _logger = logging.getLogger(logger_name)
    for _handler in _logger.handlers:
        _logger.removeHandler(_handler)
    _logger.addHandler(handler)

    if logger_name in LOG_LEVEL:
        _logger.setLevel(LOG_LEVEL[logger_name])
    else:
        _logger.setLevel(logging.WARNING)


def check_path(*args, force=False):
    """Check and create all pathes in *args

    Returns:

    """
    for _path in args:
        if exists(_path) and force:
            rmtree(_path)
        if not exists(_path):
            makedirs(_path)


def logger_add_file_handler(log_path: str):
    """Add file handler to logger

    Args:
        log_path (str): Folder to place log file
    """
    # check log save path
    check_path(log_path)

    # add file handler
    file_handler = logging.FileHandler(
        f"{log_path}/{datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')}.log")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s :: %(message)s", datefmt="%m-%d %H:%M:%S"))
    logger.addHandler(file_handler)


def rectify_domain_size(point_num: int, nest_ratio: int) -> int:
    """Rectify domain size.

    Args:
        point_num (int): Point number of one side.
        nest_ratio (int): The nesting ratio relative to the domain’s parent.

    Returns:
        int: New size.
    """
    # calculate remainder
    point_num_mod = (point_num - 1) % nest_ratio

    if point_num_mod == 0:
        return point_num

    if point_num_mod < nest_ratio / 2:
        # # point_num_mod is closer to (nest_ratio - 1) than nest_ratio
        point_num -= point_num_mod
    else:
        # # point_num_mod is closer to nest_ratio than (nest_ratio - 1)
        point_num += (nest_ratio - point_num_mod)

    return point_num


def _calculate_domain_shape(step: float, resolution: int, grid_resolution=110, nest_ratio=1) -> int:
    """Calculate domain shape based on its area

    Args:
        step (float): Length of the side. Unit: degree.
        resolution (int): Resolution of domain. Unit: km.
        grid_resolution (int, optional): Resolution of grid. Unit: km. Defaults to 110.
        nest_ratio (int, optional): The nesting ratio relative to the domain’s parent.

    Returns:
        tuple[int, int]: (length of x, length of y)
    """
    # calculate res based on doamin area and resolution
    res = int(step * grid_resolution) // resolution

    # rectify

    return rectify_domain_size(res, nest_ratio=nest_ratio)


def calculate_domain_shape(lon_step: float, lat_step: float, resolution: int, grid_resolution=110, nest_ratio=1) -> tuple[int, int]:
    """Calculate domain shape based on its area

    Args:
        lon_step (float): Length in X direction. Unit: degree.
        lat_step (float): Length in Y direction. Unit: degree.
        resolution (int): Resolution of domain. Unit: km.
        grid_resolution (int, optional): Resolution of grid. Unit: km. Defaults to 110.
        nest_ratio (int, optional): The nesting ratio relative to the domain’s parent.

    Returns:
        tuple[int, int]: (length of x, length of y)
    """

    return (
        _calculate_domain_shape(
            lon_step, resolution, grid_resolution=grid_resolution, nest_ratio=nest_ratio),
        _calculate_domain_shape(
            lat_step, resolution, grid_resolution=grid_resolution, nest_ratio=nest_ratio)
    )


def _check_domain_shape(point_num: int, nest_ratio: int) -> bool:
    """Check domain shape.

    Args:
        point_num (int): Point number of one side.
        nest_ratio (int): The nesting ratio relative to the domain’s parent.

    Returns:
        bool: True if pass check else False.
    """
    if (point_num - 1) % nest_ratio != 0:
        return False
    else:
        return True


def check_domain_shape(x_point_num: int, y_point_num: int, nest_ratio: int) -> tuple[bool, bool]:
    """Check domain shape.

    Args:
        x_point_num (int): Point number of X side.
        y_point_num (int): Point number of Y side.
        nest_ratio (int): The nesting ratio relative to the domain’s parent.

    Returns:
        tuple[bool, bool]: Tuple of bool. True if pass check else False
    """
    return (
        _check_domain_shape(x_point_num, nest_ratio=nest_ratio),
        _check_domain_shape(y_point_num, nest_ratio=nest_ratio)
    )


def check_subprocess_status(status: subprocess.CompletedProcess):
    """Check subprocess return code and print log if their return code != 0

    Args:
        status (CompletedProcess): Status from subprocess.
    """
    if status.returncode != 0:
        # print command
        command = status.args
        logger.error(f"Failed to exec command: {command}")

        # print log
        logger.error(f"====== stdout ======")
        logger.error(status.stdout.decode())
        logger.error(f"====== ====== ======")
        logger.error(f"====== stderr ======")
        logger.error(status.stderr.decode())
        logger.error(f"====== ====== ======")

        # raise error
        raise RuntimeError


def call_subprocess(command: list[str], work_path: Optional[str] = None, print_output=False):
    """
    Execute the given command in system shell.

    :param command: A list contains the command and parameters to be executed.
    :type command: list
    :param work_path: The work path of the command.
                      If None, works in current directory.
    :type work_path: str | None
    :param print_output: If print standard output and error in the logger.
    :type print_output: bool
    :return:
    :rtype:
    """
    if work_path is not None:
        origin_path = getcwd()
        chdir(work_path)
    else:
        origin_path = None

    status = subprocess.run(' '.join(command), shell=True, capture_output=True)

    if origin_path is not None:
        chdir(origin_path)

    check_subprocess_status(status)

    if print_output:
        logger.info(status.stdout.decode())
        logger.warning(status.stderr.decode())


__all__ = ["logger", "check_path", "logger_add_file_handler", "calculate_domain_shape", "rectify_domain_size", "check_domain_shape",
           "check_subprocess_status", "call_subprocess"]
