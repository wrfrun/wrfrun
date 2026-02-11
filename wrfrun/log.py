"""
wrfrun.log
##########

.. autosummary::
    :toctree: generated/

    get_wrfrun_rich_console
    logger_add_file_handler
    set_logger
    unify_logger_format

``wrfrun`` submodule to manage logs. This submodule only take care of ``wrfrun``'s log.

For functions and classes which parse numerical models' log, please check :doc:`model </api/model>`.
"""

import logging
from datetime import datetime
from time import time
from typing import Dict, List, Optional

from rich.console import Console
from rich.logging import RichHandler

from .utils import check_path

WRFRUN_RICH_CONSOLE = Console()


def set_logger(logger_list: List[str], logger_level: Optional[Dict] = None):
    """
    This function will replace all handlers of each logger in ``logger_list`` with RichHandler.

    If there are some custom handlers in logger, they will be replaced too.

    :param logger_list: A list contains loggers.
    :type logger_list: list
    :param logger_level: You can specify the log level in ``logger_level``, with the name of logger is the key,
                         and the level of logger is the value.
                         Default if None, with which all loggers' level will be set to ``logging.WARNING``.
    :type logger_level: list | None
    """
    formatter = logging.Formatter("%(name)s :: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # use rich handler
    handler = RichHandler(console=WRFRUN_RICH_CONSOLE, markup=True)
    handler.setFormatter(formatter)

    for logger_name in logger_list:
        if logger_name in logging.root.manager.loggerDict:
            _logger = logging.getLogger(logger_name)
            for _handler in _logger.handlers:
                _logger.removeHandler(_handler)
            _logger.addHandler(handler)

            if logger_level is not None and logger_name in logger_level:
                _logger.setLevel(logger_level[logger_name])
            else:
                _logger.setLevel(logging.WARNING)


def unify_logger_format():
    """
    This function is only supposed to be used internally.

    This function will replace all handlers of each logger with ``rich.logging.RichHandler``.
    Use this carefully.
    """
    set_logger(
        ["cdsapi", "cfgrib", "datapi"],
        {"cdsapi": logging.INFO, "cfgrib": logging.ERROR, "datapi": logging.INFO},
    )


# init wrfrun logger
logger = logging.getLogger("wrfrun")
# check environment variables and set logger level
# if "WRFRUN_DEBUG_MODE" in environ and environ["WRFRUN_DEBUG_MODE"]:
#     _logger_level = logging.DEBUG
#     _debug_mode = True
# else:
#     _logger_level = logging.INFO
#     _debug_mode = False
set_logger(["wrfrun"], {"wrfrun": logging.INFO})
# logger.debug(f"DEBUG MODE: {_debug_mode}")


def logger_add_file_handler(log_path: str):
    """
    Set log file of logger.

    :param log_path: Log file path.
    :type log_path: str
    """
    # check log save path
    check_path(log_path)

    # add file handler
    file_handler = logging.FileHandler(f"{log_path}/{datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')}.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s :: %(message)s", datefmt="%m-%d %H:%M:%S")
    )
    logger.addHandler(file_handler)


def get_wrfrun_rich_console() -> Console:
    """
    Get ``rich.console.Console`` instance used in wrfrun.

    :return: Console instance.
    :rtype: Console
    """
    return WRFRUN_RICH_CONSOLE


__all__ = ["set_logger", "unify_logger_format", "logger_add_file_handler", "logger", "get_wrfrun_rich_console"]
