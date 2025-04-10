from dataclasses import dataclass
from os import listdir, makedirs, remove
from os.path import basename, exists
from shutil import copyfile
from typing import Optional, TypedDict, Union

from .. import WRFRUNConfig
from ..core import ExecutableBase, LoadConfigError, OutputError
from ..utils import logger


@dataclass
class NamelistName:
    """
    Namelist file names.
    """
    WPS = "namelist.wps"
    WRF = "namelist.input"
    WRFDA = "namelist.input"


class FileConfigDict(TypedDict):
    """
    Dict class to give information to process files.
    """
    file_path: str
    save_path: Optional[str]
    save_name: Optional[str]


def generate_namelist_file(namelist_type: str, save_path: Optional[str] = None):
    """
    Write namelist to a file so WPS or WRF can use its settings.

    :param namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type registered.
    :type namelist_type: str
    :param save_path: If namelist_type isn't in ``["wps", "wrf", "wrfda"]``, ``save_path`` must be specified.
    :type save_path: str | None
    :return:
    """
    if namelist_type == "wps":
        save_path = f"{WRFRUNConfig.WPS_WORK_PATH}/{NamelistName.WPS}"
    elif namelist_type == "wrf":
        save_path = f"{WRFRUNConfig.WRF_WORK_PATH}/{NamelistName.WRF}"
    elif namelist_type == "wrfda":
        save_path = f"{WRFRUNConfig.WRFDA_WORK_PATH}/{NamelistName.WRFDA}"
    else:
        if save_path is None:
            logger.error(f"`save_path` is needed to save custom namelist.")
            raise ValueError(f"`save_path` is needed to save custom namelist.")

    WRFRUNConfig.namelist.write_namelist(save_path, namelist_type)


class ModelExecutableBase(ExecutableBase):
    """
    Base class for NWP executables.
    """

    def __init__(self, name: str, cmd: str, work_path: Optional[str] = None, mpi_use=False, mpi_cmd: Optional[str] = None, mpi_core_num: Optional[int] = None):
        """
        Base class for NWP executables.

        :param name: Unique name to identify different executables.
        :type name: str
        :param cmd: Command to execute. For example, ``"./geogrid.exe"``.
        :type cmd: str
        :param work_path: Working directory path. Defaults to None (wrfrun workspace).
        :type work_path: str
        :param mpi_use: If you use mpi. You have to give ``mpi_cmd`` and ``mpi_core_num`` if you use mpi. Defaults to False.
        :type mpi_use: bool
        :param mpi_cmd: MPI command. For example, ``"mpirun"``. Defaults to None.
        :type mpi_cmd: str
        :param mpi_core_num: How many cores you use. Defaults to None.
        :type mpi_core_num: int
        """
        if self._initialized:
            return

        super().__init__(name, cmd, work_path, mpi_use, mpi_cmd, mpi_core_num)

        self.addition_files = []
        self.save_rules = []

    def generate_custom_config(self):
        """
        Get and store namelist.

        :return:
        :rtype:
        """
        self.custom_config.update({
            "namelist": WRFRUNConfig.get_namelist("wps"),
            "addition_files": self.addition_files,
            "save_rules": self.save_rules,
        })

    def load_custom_config(self):
        if "namelist" not in self.custom_config:
            logger.error("'namelist' not found. Maybe you forget to load config or load value from a corrupted config file.")
            raise LoadConfigError("'namelist' not found. Maybe you forget to load config or load value from a corrupted config file.")
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wps")

        if "addition_files" in self.custom_config:
            self.addition_files = self.custom_config["addition_files"]

        if "save_rules" in self.custom_config:
            self.save_rules = self.custom_config["save_rules"]

    def add_addition_files(self, addition_files: Union[str, list[str], FileConfigDict, list[FileConfigDict]]):
        """
        Add addition files the NWP will use.

        You can give a single file path or a list contains files' path.

        >>> self.add_addition_files("data/custom_file")
        >>> self.add_addition_files(["data/custom_file_1", "data/custom_file_2"])

        You can give more information with a ``FileConfigDict``, like the path and the name to store.
        "save_path" and "save_name" is optional, ``self.work_path`` and file's base name will be used.

        >>> file_dict: FileConfigDict = {"file_path": "data/custom_file", "save_path": None, "save_name": None}
        >>> # self.work will replace "save_path", "custom_file" will replace "save_name" when process the file.
        >>> self.add_addition_files(file_dict)

        >>> file_dict: FileConfigDict = {"file_path": "data/custom_file", "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/geogrid", "save_name": "GEOGRID.TBL"}
        >>> self.add_addition_files(file_dict)

        >>> file_dict_1: FileConfigDict = {"file_path": "data/custom_file", "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/geogrid", "save_name": "GEOGRID.TBL"}
        >>> file_dict_2: FileConfigDict = {"file_path": "data/custom_file", "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/outputs", "save_name": "test_file"}
        >>> self.add_addition_files([file_dict_1, file_dict_2])

        :param addition_files: Custom files' path.
        :type addition_files: str | list | dict
        :return:
        :rtype:
        """
        if not isinstance(addition_files, list):
            addition_files = [addition_files, ]
        logger.debug(f"Add addition file for '{self.name}': {addition_files}")
        self.addition_files += addition_files

    def add_save_files(
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
        if output_dir is None:
            current_output_dir = self.work_path
        else:
            current_output_dir = output_dir

        if save_path is None:
            save_path = f"{WRFRUNConfig.get_output_path()}/{self.name}"

        file_list = listdir(current_output_dir)
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
                raise OutputError(f"Can't find any files match the giving rules: startswith='{startswith}', endswith='{endswith}', outputs='{outputs}'")

            else:
                return

        save_file_list = list(set(save_file_list))
        logger.debug(f"Files to be processed: {save_file_list}")

        for _file in save_file_list:
            self.save_rules.append((_file, output_dir, save_path))

    def before_call(self):
        """
        This function will copy the additional necessary files registered by ``add_addition_files`` to the workspace.

        :return:
        :rtype:
        """
        for _file_item in self.addition_files:
            if isinstance(_file_item, str):
                _file = _file_item
                _save_path = self.work_path
                _save_name = basename(_file)

            if isinstance(_file_item, FileConfigDict):
                _file = _file_item["file_path"]
                _save_path = _file_item["save_path"]
                _save_name = _file_item["save_name"]

                _save_path = self.work_path if _save_path is None else _save_path
                _save_name = basename(_file) if _save_name is None else _save_name

            else:
                logger.warning(f"Found unsupported registered file type: {type(_file_item)}. File is {_file_item}.")
                logger.warning("Skip this file.")
                continue

            logger.debug(f"Copy addition file '{_file}' to '{_save_path}'")

            if exists(f"{_save_path}/{_save_name}"):
                logger.warning(f"There is a '{_save_name}' in '{_save_path}', overwrite it")
                remove(f"{_save_path}/{_save_name}")
            copyfile(_file, f"{_save_path}/{_save_name}")

    def after_call(self):
        """
        Save file according to save rules.

        :return:
        :rtype:
        """
        for _rule in self.save_rules:
            _file, _output_path, _save_path = _rule

            if _output_path is None:
                _output_path = self.work_path

            if not exists(_save_path):
                makedirs(_save_path)

            if exists(f"{_save_path}/{_file}"):
                logger.error(f"Found existed file, which means you already have output files in '{_save_path}'")
                logger.error("Backup your results, or chose an empty directory to save results.")
                raise FileExistsError(f"Found existed file, which means you already have output files in '{_save_path}'. "
                                      "Backup your results, or chose an empty directory to save results.")

            copyfile(f"{_output_path}/{_file}", f"{_save_path}/{_file}")


__all__ = ["ModelExecutableBase", "NamelistName", "FileConfigDict"]
