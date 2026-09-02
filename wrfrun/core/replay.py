"""
wrfrun.core.replay
##################

This module provides methods to read configs from replay file and reproduce simulations.

.. autosummary::
    :toctree: generated/

    replay_config_generator
"""

import logging
from collections.abc import Generator
from json import loads
from shutil import unpack_archive

from .base import ExecutableBase
from .core import WRFRUN_NEW
from .type import ExecutableConfig

LOGGER = logging.getLogger("wrfrun")


def replay_config_generator(replay_config_file: str) -> Generator[tuple[str, ExecutableBase], None, None]:
    """
    This method can read the ``.replay`` file and returns a generator which yields ``Executable`` and their names.
    If this method doesn't find ``config.json`` in the ``.replay`` file, :class:`FileNotFoundError` will be raised.

    The ``Executable`` you get from the generator has been initialized so you can execute it directly.

    >>> replay_file = "./example.replay"
    >>> for name, _exec in replay_config_generator(replay_file):
    >>>     _exec.replay()

    :param replay_config_file: Path of the ``.replay`` file.
    :type replay_config_file: str
    :return: A generator that yields: ``(name, Executable)``
    :rtype: Generator
    """
    LOGGER.info(f"Loading replay resources from: {replay_config_file}")
    work_path = WRFRUN_NEW.resource.get_custom_resource(WRFRUN_NEW.resource.REPLAY_DIR)
    simulation_json = work_path / "config.json"

    unpack_archive(replay_config_file, work_path, "zip")

    if not simulation_json.exists():
        LOGGER.error("Can't find replay config in the provided config file.")
        raise FileNotFoundError("Can't find replay config in the provided config file.")

    with open(simulation_json, "r") as f:
        replay_config_list: list[ExecutableConfig] = loads(f.read())

    for _config in replay_config_list:
        args = _config["class_config"]["class_args"]
        kwargs = _config["class_config"]["class_kwargs"]
        executable: ExecutableBase = WRFRUN_NEW.registry.get_cls(_config["name"])(*args, **kwargs)
        executable.load_config(_config)
        yield _config["name"], executable


__all__ = ["replay_config_generator"]
