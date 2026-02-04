"""
wrfrun.core.type
#################

Define custom types.

.. autosummary::
    :toctree: generated/

    InputFileType
    FileConfigDict
    ExecutableClassConfig
    ExecutableConfig
"""

from enum import Enum
from typing import Optional, TypedDict, Union


class InputFileType(Enum):
    """
    This class is an ``Enum`` class, providing the following values:

    .. py:attribute:: WRFRUN_RES
        :type: int
        :value: 1

        Indicating resource files are from the model or ``wrfrun``.
        ``wrfrun`` won't save these files when recording the simulation.

    .. py:attribute:: CUSTOM_RES
        :type: int
        :value: 2

        Indicating resource files are provided by the user.
        ``wrfrun`` will also save these files to ``.replay`` file
        when recording the simulation to ensure the simulation is replayable.
    """

    WRFRUN_RES = 1
    CUSTOM_RES = 2


class FileConfigDict(TypedDict):
    """
    This dict is used to store information about the file, including its path,
    the path it will be copied or moved to, its new name, etc.
    This dict contains following keys:

    .. py:attribute:: file_path
        :type: str

        A real file path or a valid URI which can be converted to a file path.

    .. py:attribute:: save_path
        :type: str

        Save path of the file.

    .. py:attribute:: save_name
        :type: str

        Save name of the file.

    .. py:attribute:: is_data
        :type: bool

        If the file is data. If not, ``wrfrun`` will treat it as a config file,
        and always save it to ``.replay`` file when recording the simulation.

    .. py:attribute:: is_output
        :type: bool

        If the file is model's output. Output file will never be saved to ``.replay`` file.
    """

    file_path: str
    save_path: str
    save_name: str
    is_data: bool
    is_output: bool


class ExecutableClassConfig(TypedDict):
    """
    This dict is used to store arguments of ``Executable``'s ``__init__`` function.

    .. py:attribute:: class_args
        :type: tuple

        Positional arguments of the class.

    .. py:attribute:: class_kwargs
        :type: dict

        Keyword arguments of the class.
    """

    # only list essential config
    class_args: tuple
    class_kwargs: dict


class ExecutableConfig(TypedDict):
    """
    This dict is used to store all configs of a :class:`ExecutableBase`.

    .. py:attribute:: name
        :type: str

        Name of the executable. Each type of executable has a unique name.

    .. py:attribute:: cmd
        :type: str | list[str]

        Command of the executable.

    .. py:attribute:: work_path
        :type: str | None

        Work path of the executable.

    .. py:attribute:: mpi_use
        :type: bool

        If the executable will use MPI.

    .. py:attribute:: mpi_cmd
        :type: str | None

        Command name of the MPI.

    .. py:attribute:: mpi_core_num
        :type: int | None

        Number of the CPU core to use with MPI.

    .. py:attribute:: class_config
        :type: ExecutableClassConfig | None

        A dict stores arguments of ``Executable``'s ``__init__`` function.

    .. py:attribute:: input_file_config
        :type: list[FileConfigDict] | None

        A list stores information about input files of the executable.

    .. py:attribute:: output_file_config
        :type: list[FileConfigDict] | None

        A list stores information about output files of the executable.

    .. py:attribute:: custom_config
        :type: dict | None

        A dict that can be used by subclass to store other configs.
    """

    name: str
    cmd: Union[str, list[str]]
    work_path: Optional[str]
    mpi_use: bool
    mpi_cmd: Optional[str]
    mpi_core_num: Optional[int]
    class_config: ExecutableClassConfig
    input_file_config: list[FileConfigDict]
    output_file_config: list[FileConfigDict]
    custom_config: dict


__all__ = ["InputFileType", "FileConfigDict", "ExecutableClassConfig", "ExecutableConfig"]
