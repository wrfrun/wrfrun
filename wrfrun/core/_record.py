"""
wrfrun.core._record
###################

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

from json import dumps
from os import makedirs, remove
from os.path import basename, dirname, exists, isdir
from shutil import copyfile, make_archive, move

import numpy as np

from ..log import check_path, logger
from ._config import WRFRunConfig
from .type import ExecutableConfig


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


class ExecutableRecorder:
    """
    This class provides methods to record simulations.
    """

    def __init__(self, wrfrun_config: WRFRunConfig, save_path="./wrfrun.replay", include_data=False):
        """
        :param wrfrun_config: `WRFRunConfig` instance.
        :type wrfrun_config: WRFRunConfig
        :param save_path: Save path of the replay file, defaults to "./wrfrun.replay"
        :type save_path: str, optional
        :param include_data: If includes data files, defaults to False
        :type include_data: bool, optional
        """
        self._wrfrun_config = wrfrun_config

        self.save_path = save_path
        self.include_data = include_data

        self.work_path = self._wrfrun_config.parse_resource_uri(self._wrfrun_config.WRFRUN_WORKSPACE_REPLAY)
        self.content_path = f"{self.work_path}/config_and_data"

        self._recorded_config = []
        self._name_count = {}

    def record(self, exported_config: ExecutableConfig):
        """
        Record exported config for replay.

        :param exported_config: Executable config.
        :type exported_config: ExecutableConfig
        """
        if not self.include_data:
            self._recorded_config.append(exported_config)
            return

        check_path(self.content_path)

        # process exported config so we can also include data.
        # create directory to place data
        name = exported_config["name"]
        if name in self._name_count:
            self._name_count[name] += 1
            index = self._name_count[name]
        else:
            self._name_count[name] = 1
            index = 1

        data_save_uri = f"{self._wrfrun_config.WRFRUN_WORKSPACE_REPLAY}/{name}/{index}"
        data_save_path = f"{self.content_path}/{name}/{index}"
        makedirs(data_save_path)

        input_file_config = exported_config["input_file_config"]

        for _config_index, _config in enumerate(input_file_config):
            if not _config["is_data"]:
                continue

            if _config["is_output"]:
                continue

            file_path = _config["file_path"]
            file_path = self._wrfrun_config.parse_resource_uri(file_path)
            filename = basename(file_path)
            copyfile(file_path, f"{data_save_path}/{filename}")

            _config["file_path"] = f"{data_save_uri}/{filename}"
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
            logger.debug(f"Change save path to: {save_path}")
            self.save_path = save_path

        if include_data is not None:
            self.include_data = include_data

    def export_replay_file(self):
        """
        Save replay file to the save path.
        """
        if len(self._recorded_config) == 0:
            logger.warning("No replay config has been recorded.")
            return

        logger.info("Exporting replay config... It may take a few minutes if you include data.")

        check_path(self.content_path)

        with open(f"{self.content_path}/config.json", "w") as f:
            f.write(dumps(self._recorded_config, indent=4, default=_json_default))

        if exists(self.save_path):
            if isdir(self.save_path):
                self.save_path = f"{self.save_path}/wrfrun.replay"
            else:
                if not self.save_path.endswith(".replay"):
                    self.save_path = f"{self.save_path}.replay"

                if exists(self.save_path):
                    logger.warning(f"Found existed replay file with the same name '{basename(self.save_path)}', overwrite it")
                    remove(self.save_path)

        if not exists(dirname(self.save_path)):
            makedirs(dirname(self.save_path))

        temp_file = f"{self.work_path}/config_and_data"
        make_archive(temp_file, "zip", self.content_path)
        move(f"{temp_file}.zip", self.save_path)

        logger.info(f"Replay config exported to {self.save_path}")


__all__ = ["ExecutableRecorder"]
