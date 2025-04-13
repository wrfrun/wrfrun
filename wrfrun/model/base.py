from dataclasses import dataclass
from os import listdir
from os.path import basename
from typing import Optional, Union

from ..core import ExecutableBase, FileConfigDict, LoadConfigError, OutputFileError, WRFRUNConfig
from ..utils import logger


@dataclass
class NamelistName:
    """
    Namelist file names.
    """
    WPS = "namelist.wps"
    WRF = "namelist.input"
    WRFDA = "namelist.input"


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

    def __init__(self, name: str, cmd: Union[str, list[str]], work_path: Optional[str] = None, mpi_use=False, mpi_cmd: Optional[str] = None, mpi_core_num: Optional[int] = None):
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

        self.input_file_wrfrun = []

    def generate_custom_config(self):
        """
        Get and store namelist.

        :return:
        :rtype:
        """
        self.custom_config.update({
            "namelist": WRFRUNConfig.get_namelist("wps"),
        })

    def load_custom_config(self):
        if "namelist" not in self.custom_config:
            logger.error("'namelist' not found. Maybe you forget to load config or load value from a corrupted config file.")
            raise LoadConfigError("'namelist' not found. Maybe you forget to load config or load value from a corrupted config file.")
        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "wps")

    def add_input_files(self, input_files: Union[str, list[str], FileConfigDict, list[FileConfigDict]], is_data=True):
        """
        Add input files the NWP will use.

        You can give a single file path or a list contains files' path.

        >>> self.add_input_files("data/custom_file")
        >>> self.add_input_files(["data/custom_file_1", "data/custom_file_2"])

        You can give more information with a ``FileConfigDict``, like the path and the name to store, and if it is data.

        >>> file_dict: FileConfigDict = {"file_path": "data/custom_file.nc", "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}", "save_name": "custom_file.nc", "is_data": True}
        >>> self.add_input_files(file_dict)

        >>> file_dict_1: FileConfigDict = {"file_path": "data/custom_file", "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/geogrid", "save_name": "GEOGRID.TBL", "is_data": False}
        >>> file_dict_2: FileConfigDict = {"file_path": "data/custom_file", "save_path": f"{WRFRUNConfig.WPS_WORK_PATH}/outputs", "save_name": "test_file", "is_data": True}
        >>> self.add_input_files([file_dict_1, file_dict_2])

        :param input_files: Custom files' path.
        :type input_files: str | list | dict
        :param is_data: If its data. This parameter will be overwritten by the value in ``input_files``.
        :type is_data: bool
        :return:
        :rtype:
        """
        if isinstance(input_files, str):
            self.input_file_config.append({"file_path": input_files, "save_path": self.work_path, "save_name": basename(input_files), "is_data": is_data})

        elif isinstance(input_files, list):
            for _file in input_files:
                if isinstance(_file, FileConfigDict):
                    self.input_file_config.append(_file)

                elif isinstance(_file, str):
                    self.input_file_config.append({"file_path": _file, "save_path": self.work_path, "save_name": basename(_file), "is_data": is_data})

                else:
                    logger.error(f"Input file config should be string or `FileConfigDict`, but got '{type(_file)}'")
                    raise TypeError(f"Input file config should be string or `FileConfigDict`, but got '{type(_file)}'")

        elif isinstance(input_files, FileConfigDict):
            self.input_file_config.append(input_files)

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
        if output_dir is None:
            output_dir = self.work_path

        if save_path is None:
            save_path = f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/{self.name}"

        file_list = listdir(WRFRUNConfig.parse_wrfrun_uri(output_dir))
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
            self.output_file_config.append({"file_path": f"{output_dir}/{_file}", "save_path": save_path, "save_name": _file, "is_data": True})


__all__ = ["ModelExecutableBase", "NamelistName"]
