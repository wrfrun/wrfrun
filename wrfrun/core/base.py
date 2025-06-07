import subprocess
from enum import Enum
from json import dumps
from os import chdir, getcwd, listdir, makedirs, remove, symlink
from os.path import abspath, basename, dirname, exists, isdir
from shutil import copyfile, make_archive, move
from typing import Optional, TypedDict, Union

import numpy as np

from .config import WRFRUNConfig
from .error import CommandError, ConfigError, OutputFileError
from ..utils import check_path, logger


def check_subprocess_status(status: subprocess.CompletedProcess):
    """
    Check subprocess return code and print log if ``return_code != 0``.

    :param status: Status from subprocess.
    :type status: CompletedProcess
    """
    if status.returncode != 0:
        # print command
        command = status.args
        logger.error(f"Failed to exec command: {command}")

        # print log
        logger.error("====== stdout ======")
        logger.error(status.stdout.decode())
        logger.error("====== ====== ======")
        logger.error("====== stderr ======")
        logger.error(status.stderr.decode())
        logger.error("====== ====== ======")

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


class InputFileType(Enum):
    """
    Input file type.
    ``WRFRUN_RES`` means the input file is from the NWP or wrfrun package.
    ``CUSTOM_RES`` means the input file is from the user, which may be a customized file.
    """
    WRFRUN_RES = 1
    CUSTOM_RES = 2


class FileConfigDict(TypedDict):
    """
    Dict class to give information to process files.
    """
    file_path: str
    save_path: str
    save_name: str
    is_data: bool
    is_output: bool


class ExecutableClassConfig(TypedDict):
    """
    Executable class initialization config template.
    """
    # only list essential config
    class_args: tuple
    class_kwargs: dict


class ExecutableConfig(TypedDict):
    """
    Executable config template.
    """
    name: str
    cmd: Union[str, list[str]]
    work_path: Optional[str]
    mpi_use: bool
    mpi_cmd: Optional[str]
    mpi_core_num: Optional[int]
    class_config: Optional[ExecutableClassConfig]
    input_file_config: Optional[list[FileConfigDict]]
    output_file_config: Optional[list[FileConfigDict]]
    custom_config: Optional[dict]


class _ExecutableConfigRecord:
    """
    Record executable configs and export them.
    """
    _instance = None
    _initialized = False

    def __init__(self, save_path: Optional[str] = None, include_data=False):
        """
        Record executable configs and export them.

        :param save_path: Save path of the exported config file.
        :type save_path: str
        :param include_data: If includes input data.
        :type include_data: bool
        """

        if self._initialized:
            return

        if save_path is None:
            WRFRUNConfig.IS_RECORDING = False
        else:
            WRFRUNConfig.IS_RECORDING = True

        self.save_path = save_path
        self.include_data = include_data

        self.work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_REPLAY_WORK_PATH)
        self.content_path = f"{self.work_path}/config_and_data"
        check_path(self.content_path)

        self._recorded_config = []
        self._name_count = {}

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def reinit(self, save_path: Optional[str] = None, include_data=False):
        """
        Reinitialize this instance.

        :return:
        :rtype:
        """
        self._initialized = False
        return _ExecutableConfigRecord(save_path, include_data)

    def record(self, exported_config: ExecutableConfig):
        """
        Record exported config for replay.

        :param exported_config: Executable config.
        :type exported_config: ExecutableConfig
        :return:
        :rtype:
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

        data_save_uri = f"{WRFRUNConfig.WRFRUN_REPLAY_WORK_PATH}/{name}/{index}"
        data_save_path = f"{self.content_path}/{name}/{index}"
        makedirs(data_save_path)

        input_file_config = exported_config["input_file_config"]

        for _config_index, _config in enumerate(input_file_config):
            if not _config["is_data"]:
                continue

            if _config["is_output"]:
                continue

            file_path = _config["file_path"]
            file_path = WRFRUNConfig.parse_resource_uri(file_path)
            filename = basename(file_path)
            copyfile(file_path, f"{data_save_path}/{filename}")

            _config["file_path"] = f"{data_save_uri}/{filename}"
            input_file_config[_config_index] = _config

        exported_config["input_file_config"] = input_file_config
        self._recorded_config.append(exported_config)

    def clear_records(self):
        """
        Clean old configs.

        :return:
        :rtype:
        """
        self._recorded_config = []

    def export_replay_file(self):
        """
        Save replay file to the specific save path.

        :return:
        :rtype:
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
                self.save_path = f"{self.save_path}/1.replay"
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


ExecConfigRecorder = _ExecutableConfigRecord()


class ExecutableBase:
    """
    Base class for all executables.
    """
    _instance = None

    def __init__(self, name: str, cmd: Union[str, list[str]], work_path: str, mpi_use=False, mpi_cmd: Optional[str] = None, mpi_core_num: Optional[int] = None):
        """
        Base class for all executables.

        :param name: Unique name to identify different executables.
        :type name: str
        :param cmd: Command to execute, can be a single string or a list contains the command and its parameters.
                    For example, ``"./geogrid.exe"``, ``["./link_grib.csh", "data/*", "."]``.
                    If you want to use mpi, then ``cmd`` must be a string.
        :type cmd: str
        :param work_path: Working directory path.
        :type work_path: str
        :param mpi_use: If you use mpi. You have to give ``mpi_cmd`` and ``mpi_core_num`` if you use mpi. Defaults to False.
        :type mpi_use: bool
        :param mpi_cmd: MPI command. For example, ``"mpirun"``. Defaults to None.
        :type mpi_cmd: str
        :param mpi_core_num: How many cores you use. Defaults to None.
        :type mpi_core_num: int
        """
        if mpi_use and isinstance(cmd, list):
            logger.error("If you want to use mpi, then `cmd` must be a single string.")
            raise CommandError("If you want to use mpi, then `cmd` must be a single string.")

        self.name = name
        self.cmd = cmd
        self.work_path = work_path
        self.mpi_use = mpi_use
        self.mpi_cmd = mpi_cmd
        self.mpi_core_num = mpi_core_num

        self.class_config: ExecutableClassConfig = {"class_args": (), "class_kwargs": {}}
        self.custom_config: dict = {}
        self.input_file_config: list[FileConfigDict] = []
        self.output_file_config: list[FileConfigDict] = []

        # directory to save outputs
        self._output_save_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/{self.name}"
        self._log_save_path = f"{self._output_save_path}/logs"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def generate_custom_config(self):
        """
        Generate custom configs.

        :return:
        :rtype:
        """
        logger.debug(f"Method 'generate_custom_config' not implemented in '{self.name}'")

    def load_custom_config(self):
        """
        Load custom configs.

        :return:
        :rtype:
        """
        logger.debug(f"Method 'load_custom_config' not implemented in '{self.name}'")

    def export_config(self) -> ExecutableConfig:
        """
        Export config of this executable.

        :return: A dict contains configs.
        :rtype: ExecutableConfig
        """
        self.generate_custom_config()

        return {
            "name": self.name,
            "cmd": self.cmd,
            "work_path": self.work_path,
            "mpi_use": self.mpi_use,
            "mpi_cmd": self.mpi_cmd,
            "mpi_core_num": self.mpi_core_num,
            "class_config": self.class_config,
            "custom_config": self.custom_config,
            "input_file_config": self.input_file_config,
            "output_file_config": self.output_file_config
        }

    def load_config(self, config: ExecutableConfig):
        """
        Load config from a dict.

        :param config: Config dict. It must contain some essential keys. Check ``ExecutableConfig`` for details.
        :type config: ExecutableConfig
        :return:
        :rtype:
        """
        if "name" not in config:
            logger.error("A valid config is required. Please check ``ExecutableConfig``.")
            raise ValueError("A valid config is required. Please check ``ExecutableConfig``.")

        if self.name != config["name"]:
            logger.error(f"Config belongs to '{config['name']}', not {self.name}")
            raise ConfigError(f"Config belongs to '{config['name']}', not {self.name}")

        self.cmd = config["cmd"]
        self.work_path = config["work_path"]
        self.mpi_use = config["mpi_use"]
        self.mpi_cmd = config["mpi_cmd"]
        self.mpi_core_num = config["mpi_core_num"]
        self.class_config = config["class_config"]
        self.custom_config = config["custom_config"]
        self.input_file_config = config["input_file_config"]
        self.output_file_config = config["output_file_config"]

        self.load_custom_config()

    def replay(self):
        """
        This method will be called when replay the simulation.
        This method should take care every job that will be done when replaying the simulation.

        :return:
        :rtype:
        """
        logger.debug(f"Method 'replay' not implemented in '{self.name}', fall back to default action.")
        self()

    def add_input_files(self, input_files: Union[str, list[str], FileConfigDict, list[FileConfigDict]], is_data=True, is_output=True):
        """
        Add input files the extension will use.

        You can give a single file path or a list contains files' path.

        >>> self.add_input_files("data/custom_file")
        >>> self.add_input_files(["data/custom_file_1", "data/custom_file_2"])

        You can give more information with a ``FileConfigDict``, like the path and the name to store, and if it is data.

        >>> file_dict: FileConfigDict = {
        ...     "file_path": "data/custom_file.nc",
        ...     "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}",
        ...     "save_name": "custom_file.nc",
        ...     "is_data": True,
        ...     "is_output": False
        ... }
        >>> self.add_input_files(file_dict)

        >>> file_dict_1: FileConfigDict = {
        ...     "file_path": "data/custom_file",
        ...     "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/geogrid",
        ...     "save_name": "GEOGRID.TBL",
        ...     "is_data": False,
        ...     "is_output": False
        ... }
        >>> file_dict_2: FileConfigDict = {
        ...     "file_path": "data/custom_file",
        ...     "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/outputs",
        ...     "save_name": "test_file",
        ...     "is_data": True,
        ...     "is_output": True
        ... }
        >>> self.add_input_files([file_dict_1, file_dict_2])

        :param input_files: Custom files' path.
        :type input_files: str | list | dict
        :param is_data: If its data. This parameter will be overwritten by the value in ``input_files``.
        :type is_data: bool
        :return:
        :rtype:
        """
        if isinstance(input_files, str):
            self.input_file_config.append(
                {
                    "file_path": input_files, "save_path": self.work_path, "save_name": basename(input_files),
                    "is_data": is_data, "is_output": is_output
                }
            )

        elif isinstance(input_files, list):
            for _file in input_files:
                if isinstance(_file, dict):
                    self.input_file_config.append(_file)  # type: ignore

                elif isinstance(_file, str):
                    self.input_file_config.append(
                        {
                            "file_path": _file, "save_path": self.work_path, "save_name": basename(_file),
                            "is_data": is_data, "is_output": is_output
                        }
                    )

                else:
                    logger.error(f"Input file config should be string or `FileConfigDict`, but got '{type(_file)}'")
                    raise TypeError(f"Input file config should be string or `FileConfigDict`, but got '{type(_file)}'")

        elif isinstance(input_files, dict):
            self.input_file_config.append(input_files)  # type: ignore

        else:
            logger.error(f"Input file config should be string or `FileConfigDict`, but got '{type(input_files)}'")
            raise TypeError(f"Input file config should be string or `FileConfigDict`, but got '{type(input_files)}'")

    def add_output_files(
        self, output_dir: Optional[str] = None, save_path: Optional[str] = None, startswith: Union[None, str, tuple[str, ...]] = None,
        endswith: Union[None, str, tuple[str, ...]] = None, outputs: Union[None, str, list[str]] = None, no_file_error=True
    ):
        """
        Add save file rules.

        :param output_dir: Output dir paths.
        :type output_dir: str
        :param save_path: Save path.
        :type save_path: str
        :param startswith: Prefix string or prefix list of output files.
        :type startswith: str | list
        :param endswith: Postfix string or Postfix list of output files.
        :type endswith: str | list
        :param outputs: Files name list. All files in the list will be saved.
        :type outputs: str | list
        :param no_file_error: If True, an error will be raised with the ``error_message``. Defaults to True.
        :type no_file_error: bool
        :return:
        :rtype:
        """
        if WRFRUNConfig.FAKE_SIMULATION_MODE:
            return

        if output_dir is None:
            output_dir = self.work_path

        if save_path is None:
            save_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/{self.name}"

        file_list = listdir(WRFRUNConfig.parse_resource_uri(output_dir))
        save_file_list = []

        if startswith is not None:
            _list = []
            for _file in file_list:
                if _file.startswith(startswith):
                    _list.append(_file)
            save_file_list += _list

            logger.debug(f"Collect files match `startswith`: {_list}")

        if endswith is not None:
            _list = []
            for _file in file_list:
                if _file.endswith(endswith):
                    _list.append(_file)
            save_file_list += _list

            logger.debug(f"Collect files match `endswith`: {_list}")

        if outputs is not None:
            if isinstance(outputs, str) and outputs in file_list:
                save_file_list.append(outputs)
            else:
                outputs = [x for x in outputs if x in file_list]
                save_file_list += outputs

        if len(save_file_list) < 1:
            if no_file_error:
                logger.error(f"Can't find any files match the giving rules: startswith='{startswith}', endswith='{endswith}', outputs='{outputs}'")
                raise OutputFileError(f"Can't find any files match the giving rules: startswith='{startswith}', endswith='{endswith}', outputs='{outputs}'")

            else:
                logger.warning(f"Can't find any files match the giving rules: startswith='{startswith}', endswith='{endswith}', outputs='{outputs}'. Skip it.")
                return

        save_file_list = list(set(save_file_list))
        logger.debug(f"Files to be processed: {save_file_list}")

        for _file in save_file_list:
            self.output_file_config.append({"file_path": f"{output_dir}/{_file}", "save_path": save_path, "save_name": _file, "is_data": True, "is_output": True})

    def before_exec(self):
        """
        Prepare input files.

        :return:
        :rtype:
        """
        if WRFRUNConfig.FAKE_SIMULATION_MODE:
            logger.info(f"We are in fake simulation mode, skip preparing input files for '{self.name}'")
            return

        for input_file in self.input_file_config:
            file_path = input_file["file_path"]
            save_path = input_file["save_path"]
            save_name = input_file["save_name"]

            file_path = WRFRUNConfig.parse_resource_uri(file_path)
            save_path = WRFRUNConfig.parse_resource_uri(save_path)

            file_path = abspath(file_path)
            save_path = abspath(save_path)

            if not exists(file_path):
                logger.error(f"File not found: '{file_path}'")
                raise FileNotFoundError(f"File not found: '{file_path}'")

            if not exists(save_path):
                makedirs(save_path)

            target_path = f"{save_path}/{save_name}"
            if exists(target_path):
                logger.debug(f"Target file {save_name} exists, overwrite it.")
                remove(target_path)

            symlink(file_path, target_path)

    def after_exec(self):
        """
        Save outputs and logs.
        
        :return: 
        :rtype: 
        """
        if WRFRUNConfig.FAKE_SIMULATION_MODE:
            logger.info(f"We are in fake simulation mode, skip saving outputs for '{self.name}'")
            return

        for output_file in self.output_file_config:
            file_path = output_file["file_path"]
            save_path = output_file["save_path"]
            save_name = output_file["save_name"]

            file_path = WRFRUNConfig.parse_resource_uri(file_path)
            save_path = WRFRUNConfig.parse_resource_uri(save_path)

            file_path = abspath(file_path)
            save_path = abspath(save_path)

            if not exists(file_path):
                logger.error(f"File not found: '{file_path}'")
                raise FileNotFoundError(f"File not found: '{file_path}'")

            if not exists(save_path):
                makedirs(save_path)

            target_path = f"{save_path}/{save_name}"
            if exists(target_path):
                logger.warning(f"Found existed file, which means you already may have output files in '{save_path}'. If you are saving logs, ignore this warning.")

            move(file_path, target_path)

    def exec(self):
        """
        Execute the given command.

        :return:
        :rtype:
        """
        work_path = WRFRUNConfig.parse_resource_uri(self.work_path)

        if not self.mpi_use or None in [self.mpi_cmd, self.mpi_core_num]:
            if isinstance(self.cmd, str):
                self.cmd = [self.cmd, ]

            logger.info(f"Running `{' '.join(self.cmd)}` ...")
            _cmd = self.cmd

        else:
            logger.info(f"Running `{self.mpi_cmd} --oversubscribe -np {self.mpi_core_num} {self.cmd}` ...")
            _cmd = [self.mpi_cmd, "--oversubscribe", "-np", str(self.mpi_core_num), self.cmd]

        if WRFRUNConfig.FAKE_SIMULATION_MODE:
            logger.info(f"We are in fake simulation mode, skip calling numerical model for '{self.name}'")
            return

        call_subprocess(_cmd, work_path=work_path)

    def __call__(self):
        """
        Execute the given command.

        :return:
        :rtype:
        """
        self.before_exec()
        self.exec()
        self.after_exec()

        if not WRFRUNConfig.IS_IN_REPLAY and WRFRUNConfig.IS_RECORDING:
            ExecConfigRecorder.record(self.export_config())


__all__ = ["ExecutableBase", "FileConfigDict", "InputFileType", "ExecutableConfig", "ExecutableClassConfig", "ExecConfigRecorder"]
