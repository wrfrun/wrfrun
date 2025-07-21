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
