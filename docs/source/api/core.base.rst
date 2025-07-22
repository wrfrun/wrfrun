wrfrun.core.base
################

.. py:class:: InputFileType[Enum]

   This class is an ``Enum`` class, providing the following values:

   .. py:attribute:: WRFRUN_RES
      :type: int
      :value: 1

      Indicating resource files are from the model or ``wrfrun``. ``wrfrun`` won't save these files when recording the simulation.

   .. py:attribute:: CUSTOM_RES
      :type: int
      :value: 2

      Indicating resource files are provided by the user. ``wrfrun`` will also save these files to ``.replay`` file when recording the simulation to ensure the simulation is replayable.

.. py:class:: FileConfigDict[TypedDict]

   This dict is used to store information about the file, including its path, the path it will be copied or moved to, its new name, etc. This dict contains following keys:

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

      If the file is data. If not, ``wrfrun`` will treat it as a config file, and always save it to ``.replay`` file when recording the simulation.

   .. py:attribute:: is_output
      :type: bool

      If the file is model's output. Output file will never be saved to ``.replay`` file.

.. py:class:: ExecutableClassConfig[TypedDict]

   This dict is used to store arguments of ``Executable``'s ``__init__`` function.

   .. py:attribute:: class_args
      :type: tuple

      Positional arguments of the class.

   .. py:attribute:: class_kwargs
      :type: dict

      Keyword arguments of the class.

.. py:class:: ExecutableBase(self, name: str, cmd: Union[str, list[str]], work_path: str, mpi_use=False, mpi_cmd: Optional[str] = None, mpi_core_num: Optional[int] = None)
    
    Base class for all executables.

    :param name: Unique name to identify different executables.
    :type name: str
    :param cmd: Command to execute, can be a single string or a list contains the command and its parameters. For example, ``"./geogrid.exe"``, ``["./link_grib.csh", "data/*", "."]``. If you want to use mpi, then ``cmd`` must be a string.
    :type cmd: str
    :param work_path: Working directory path.
    :type work_path: str
    :param mpi_use: If you use mpi. You have to give ``mpi_cmd`` and ``mpi_core_num`` if you use mpi. Defaults to False.
    :type mpi_use: bool
    :param mpi_cmd: MPI command. For example, ``"mpirun"``. Defaults to None.
    :type mpi_cmd: str
    :param mpi_core_num: How many cores you use. Defaults to None.
    :type mpi_core_num: int

    .. py:attribute:: class_config
        :type: ExecutableClassConfig
        :value: ``{"class_args": (), "class_kwargs": {}}``

    .. py:attribute:: custom_config
        :type: dict
        :value: ``{}``

    .. py:attribute:: input_file_config
        :type: list[FileConfigDict]
        :value: ``[]``

    .. py:attribute:: output_file_config
        :type: list[FileConfigDict]
        :value: ``[]``

    .. py:method:: generate_custom_config(self)
        :abstractmethod:

        Generate custom configs. This method should be overwritten in the child class, or it will do nothing except print a debug log.

    .. py:method:: load_custom_config(self)

    .. py:method:: export_config(self)

    .. py:method:: load_config(self, config: ExecutableConfig)

    .. py:method:: replay(self)

    .. py:method:: add_input_files(self, input_files: Union[str, list[str], FileConfigDict, list[FileConfigDict]], is_data=True, is_output=True)

    .. py:method:: add_output_files(self, output_dir: Optional[str] = None, save_path: Optional[str] = None, startswith: Union[None, str, tuple[str, ...]] = None, endswith: Union[None, str, tuple[str, ...]] = None, outputs: Union[None, str, list[str]] = None, no_file_error=True)

    .. py:method:: before_exec(self)

    .. py:method:: after_exec(self)

    .. py:method:: exec(self)
