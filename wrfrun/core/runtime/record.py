"""
wrfrun.core.runtime.record
##########################

.. autosummary::
    :toctree: generated/

    ExecutableRecorder

ExecutableRecorder
******************

This class provides methods to record simulations.
It will save configs and resources of ``Executable``, and input data optionally.
A file ends with ``.replay`` will be generated after finishing recording,
and users can reproduce the simulation with the ``.replay`` file.
"""

import logging
from json import dumps
from os import remove
from shutil import copyfile, make_archive, move, rmtree

import numpy as np

from ..type import ExecutableConfig
from .resource import ResourceCatalog

LOGGER = logging.getLogger("wrfrun")


def _json_default(obj):
    """
    Used for json.dumps.

    :param obj:
    :type obj:
    :return:
    :rtype:
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable.")


class RecordService:
    """
    This class provides methods to record simulations.
    """

    def __init__(self, resource: ResourceCatalog, save_path="./wrfrun.replay", include_data=False):
        """
        :param wrfrun_config: `WRFRunConfig` instance.
        :type wrfrun_config: WRFRunConfig
        :param save_path: Save path of the replay file, defaults to "./wrfrun.replay"
        :type save_path: str, optional
        :param include_data: If includes data files, defaults to False
        :type include_data: bool, optional
        """
        self._resource = resource

        self.save_path = save_path
        self.include_data = include_data

        self.work_path = self._resource.get_custom_resource(self._resource.REPLAY_DIR)
        self.content_path = self.work_path / "config_and_data"
        self.content_path.mkdir(exist_ok=True, parents=True)

        self._recorded_config = []
        self._name_count = {}

    def set_save_path(self, save_path: str):
        """
        Set replay file save path.

        :param save_path: File save path.
        :type save_path: str
        """
        self.save_path = save_path

    def set_include_data(self, include_data: bool):
        """
        Set if include data.

        :param include_data: If include data.
        :type include_data: bool
        """
        self.include_data = include_data

    def record(self, exported_config: ExecutableConfig):
        """
        Record exported config for replay.

        :param exported_config: Executable config.
        :type exported_config: ExecutableConfig
        """
        if not self.include_data:
            self._recorded_config.append(exported_config)
            return

        # process exported config so we can also include data.
        # create directory to place data
        name = exported_config["name"]
        if name in self._name_count:
            self._name_count[name] += 1
            index = self._name_count[name]
        else:
            self._name_count[name] = 1
            index = 1

        data_save_uri = f"{name}/{index}"
        data_save_path = self.content_path / data_save_uri
        data_save_path.mkdir(parents=True)

        input_file_config = exported_config["input_file_config"]

        for _config_index, _config in enumerate(input_file_config):
            if not _config["is_data"]:
                continue

            if _config["is_output"]:
                continue

            file_path = _config["file_path"]
            file_path = self._resource.get_custom_resource(file_path, check=True)
            copyfile(file_path, data_save_path / file_path.name)

            _config["file_path"] = f"{data_save_uri}/{file_path.name}"
            input_file_config[_config_index] = _config

        exported_config["input_file_config"] = input_file_config
        self._recorded_config.append(exported_config)

    def clear_records(self):
        """
        Clean recorded configs.
        """
        self._recorded_config = []

    def set_recorder(self, save_path: str | None, include_data: bool | None):
        """
        Change recorder settings.

        :param save_path: Save path of the exported config file.
        :type save_path: str | None
        :param include_data: If includes input data.
        :type include_data: bool | None
        """
        if save_path is not None:
            LOGGER.debug(f"Change save path to: {save_path}")
            self.save_path = save_path

        if include_data is not None:
            self.include_data = include_data

    def export_replay_file(self):
        """
        Save replay file to the save path.
        """
        if len(self._recorded_config) == 0:
            LOGGER.warning("No replay config has been recorded.")
            return

        LOGGER.info("Exporting replay config... It may take a few minutes if you include data.")

        with open(f"{self.content_path}/config.json", "w") as f:
            f.write(dumps(self._recorded_config, indent=4, default=_json_default))

        save_path = self._resource.get_custom_resource(self.save_path)

        if save_path.exists():
            LOGGER.warning("Found existed replay file, it will be overwrote.")

            if save_path.is_file():
                remove(save_path)
            else:
                rmtree(save_path)

        if save_path.suffix != ".replay":
            save_path = save_path.with_name(f"{save_path.name}.replay")

        save_path.parent.mkdir(exist_ok=True, parents=True)

        temp_file = self.work_path / "config_and_data"
        make_archive(temp_file, "zip", self.content_path)
        move(f"{temp_file}.zip", save_path)

        LOGGER.info(f"Replay config exported to {save_path}")


__all__ = ["RecordService"]
