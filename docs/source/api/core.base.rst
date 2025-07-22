wrfrun.core.base
################


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
