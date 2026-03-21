Define custom ``Executable``
#############################

This tutorial will teach you how to define a custom ``Executable``. An ``Executable`` is the part of ``wrfrun`` that interacts with external resources (for example, external programs, datasets, etc.). Classes like :class:`GeoGrid <wrfrun.model.wrf.core.GeoGrid>` are examples of ``Executable``.

By defining an ``Executable``, you define how to handle the input, execution, and output of an external program. This allows ``wrfrun`` to precisely control the execution of external programs, and also record and replay the execution of the ``Executable`` through the ``replay`` feature.

Background
**********

In ``wrfrun``, all ``Executable`` classes inherit from the same parent class :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`. When initializing the class, you must provide the following three parameters to the parent class: ``name``, ``cmd``, and ``work_path``.

* ``name``: A string used to uniquely identify this ``Executable`` to ``wrfrun``.
* ``cmd``: A string or a list of strings containing the external command and its parameters to execute.
* ``work_path``: The working path where ``wrfrun`` executes the external command.

In addition, :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` accepts three keyword parameters:

* ``mpi_use``: Boolean, whether to use MPI, defaults to ``False``.
* ``mpi_cmd``: String, the MPI command, typically ``mpirun``.
* ``mpi_core_num``: The number of CPU cores allocated when running the program with MPI.

In this tutorial, we'll temporarily ignore these last three parameters, as we assume we're defining an ``Executable`` for a simple external script ``test.py``. The script simply reads from ``input.txt`` and writes "Hello from output!" followed by the read content to ``output.txt``:

.. code-block:: python
    :caption: test.py

    with open("input.txt", "r") as f1:
        with open("output.txt", "w") as f2:

            f2.write("Hello from output!\n")
            f2.write(f1.read())

The content of ``input.txt`` is:

.. code-block:: text
    :caption: input.txt

    Hello from input!

Class Initialization
********************

First, we inherit from the parent class :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` and perform the necessary initialization. 
If you don't know what ``work_path`` should be, you can use the temporary working path defined internally by ``wrfrun``, ``WRFRUN_TEMP_PATH``, 
which can be accessed by global variable :py:data:`WRFRUN <wrfrun.core.core.WRFRUN>`: ``WRFRUN.config.WRFRUN_TEMP_PATH``.

.. code-block:: python
    :caption: main.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class Test(ExecutableBase):
        def __init__(self):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)

Adding Input Files
******************

Now, let's add the input file that our executable needs:

.. code-block:: python
    :caption: main.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class Test(ExecutableBase):
        def __init__(self, input_file: str):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
            self.input_file = input_file

        def before_exec(self):
            # Add the input file before execution
            self.add_input_files(self.input_file)

            super().before_exec()

The :py:meth:`add_input_files <wrfrun.core.base.ExecutableBase.add_input_files>` method can accept:

- A single file path string
- A list of file paths
- A dictionary with detailed file configuration
- A list of dictionaries

When running an external program, ``Executable`` assumes by default that the corresponding external program has already been placed in the corresponding workspace by the workspace preparation function. 
In this simple example, we use :py:meth:`add_input_files <wrfrun.core.base.ExecutableBase.add_input_files>` to place the Python program we wrote into the workspace first.

.. code-block:: python
    :caption: main.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class Test(ExecutableBase):
        def __init__(self, input_file: str):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
            self.input_file = input_file

        def before_exec(self):
            # Add the input file before execution
            self.add_input_files(self.input_file)
            
            # Place the Python program
            self.add_input_files("./test.py")

            super().before_exec()

Collecting Output Files
************************

Next, let's collect the output files after execution:

.. code-block:: python
    :caption: main.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class Test(ExecutableBase):
        def __init__(self, input_file: str):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
            self.input_file = input_file

        def before_exec(self):
            self.add_input_files(self.input_file)
            
            # Place the Python program
            self.add_input_files("./test.py")

            super().before_exec()

        def after_exec(self):
            # Collect the output file after execution
            self.add_output_files(outputs="output.txt")

            super().after_exec()

The ``add_output_files`` method has several useful parameters:

- ``outputs``: Specific file names to save
- ``startswith``: Prefix of files to save
- ``endswith``: Suffix of files to save
- ``output_dir``: Directory to search for outputs (defaults to work_path)
- ``save_path``: Directory to save outputs (defaults to the standard output directory)

Generating and Loading Custom Config
*************************************

To support the replay feature, we need to implement ``generate_custom_config`` and ``load_custom_config`` methods:

.. code-block:: python
    :caption: main.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class Test(ExecutableBase):
        def __init__(self, input_file: str):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
            self.input_file = input_file
            # Store initialization arguments for replay
            self.class_config["class_args"] = (input_file,)

        def before_exec(self):
            self.add_input_files(self.input_file)
            
            # Place the Python program
            self.add_input_files("./test.py")

            super().before_exec()

        def after_exec(self):
            self.add_output_files(outputs="output.txt")

            super().after_exec()

        def generate_custom_config(self):
            # Store any custom configuration needed
            self.custom_config["input_file"] = self.input_file

        def load_custom_config(self):
            # Load custom configuration during replay
            self.input_file = self.custom_config["input_file"]

Creating ``wrfrun`` Config File
*******************************

``wrfrun`` needs to read runtime settings and model-specific configurations from a :doc:`TOML configuration file </documentation/config_file>`. 
For now, we create a very simple config file to make our ``Executable`` work.

.. code-block:: toml
    :caption: config.toml

    # wrfrun work directory.
    work_dir = "./.wrfrun"
    
    # Path of the directory to store all outputs.
    output_path = "./outputs"
    log_path = "./logs"

    # Settings below won't be used for now.

    input_data_path = ""
    server_host = "localhost"
    server_port = 54321
    core_num = 1

    [job_scheduler]
    job_scheduler = "pbs"
    queue_name = ""
    node_num = 1
    env_settings = {}
    python_interpreter = "/usr/bin/python3"     # or just "python3"
    
    [model]
    [model.wrf]
    use = false
    include = "./configs/wrf.toml"
    
    [model.palm]
    use = false
    include = "./configs/palm.toml"

Complete Example
****************

By now, you should have three files in the same direcory: ``main.py``, ``test.py``, ``config.toml`` and ``input.txt``.

Here's the complete example with everything put together:

.. code-block:: python
    :caption: main.py

    import os
    from wrfrun.core import ExecutableBase, WRFRUN
    from wrfrun.run import WRFRun

    class Test(ExecutableBase):
        def __init__(self, input_file: str):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
            self.input_file = input_file
            self.class_config["class_args"] = (input_file,)

        def before_exec(self):
            self.add_input_files(self.input_file)
            
            # Place the Python program
            self.add_input_files("./test.py")

            super().before_exec()

        def after_exec(self):
            self.add_output_files(outputs="output.txt")

            super().after_exec()

        def generate_custom_config(self):
            self.custom_config["input_file"] = self.input_file

        def load_custom_config(self):
            self.input_file = self.custom_config["input_file"]

    
    if __name__ == '__main__':
        with WRFRun("./config.toml") as wrf_run:
            test_exectuable = Test("./input.txt")
            test_exectuable()

.. code-block:: python
    :caption: test.py

    with open("input.txt", "r") as f1:
        with open("output.txt", "w") as f2:

            f2.write("Hello from output!\n")
            f2.write(f1.read())

.. code-block:: text
    :caption: input.txt

    Hello from input!

Running Your ``Executable``
***************************

By running command ``python main.py``, you can see the output from ``wrfrun``

.. code-block:: bash
    :caption: output

    2026-03-21 18:04:38 INFO     wrfrun :: Read config: '/home/syize/Documents/Python/test/./config.toml'                                core.py:169
                        INFO     wrfrun :: Logger debug mode is off.                                                                   _debug.py:152
                        WARNING  wrfrun :: It seems you forget to set 'input_data_path', set it to 'data'.                            _config.py:163
                        INFO     wrfrun :: Initialize main workspace at: '/home/syize/Documents/Python/test/.wrfrun/workspace'            core.py:47
                        INFO     wrfrun :: Running python test.py ...                                                                    base.py:597

Three directories have been created by ``wrfrun``: ``.wrfrun``, ``logs`` and ``outputs``. 
You will find a log file under ``logs``, and the output of your ``Executable`` under ``outputs``.

Recording Your ``Executable``
*****************************

If you have implemented :py:meth:`before_exec <wrfrun.core.base.ExecutableBase.before_exec>` and :py:meth:`after_exec <wrfrun.core.base.ExecutableBase.after_exec>`, 
``wrfrun`` can record your ``Executable``, and generate a ``.replay`` file.

.. code-block:: python
    :caption: main.py

    import os
    from wrfrun.core import ExecutableBase, WRFRUN
    from wrfrun.run import WRFRun

    class Test(ExecutableBase):
        def __init__(self, input_file: str):
            super().__init__(name="test", cmd=["python", "test.py"], work_path=WRFRUN.config.WRFRUN_TEMP_PATH)
            self.input_file = input_file
            self.class_config["class_args"] = (input_file,)

        def before_exec(self):
            # If you want to wrfrun copy the input file into the replay file,
            # set is_output=False, and include_data=True in function record_simulation
            self.add_input_files(self.input_file, is_output=True)
            
            # Place the Python program
            self.add_input_files("./test.py")

            super().before_exec()

        def after_exec(self):
            self.add_output_files(outputs="output.txt")

            super().after_exec()

        def generate_custom_config(self):
            self.custom_config["input_file"] = self.input_file

        def load_custom_config(self):
            self.input_file = self.custom_config["input_file"]

    
    if __name__ == '__main__':
        with WRFRun("./config.toml") as wrf_run:
            # Tell wrfrun to record the simulation here,
            # and generate a replay file called test.replay
            # If you want wrfrun to also save input file to the replay file, 
            # set include_data=True
            wrf_run.record_simulation("./test.replay", include_data=False)

            test_exectuable = Test("./input.txt")
            test_exectuable()

A ``test.replay`` file will be generated. It contains all settings to call your ``Executable``, 
and input data if you set related parameters.

Advanced: Using MPI
********************

For programs that require MPI, here's a simple example about how to set it up:

.. code-block:: python
    :caption: mpi_example.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class MPIProgram(ExecutableBase):
        def __init__(self, core_num: int = 4):
            super().__init__(
                name="mpi_program",
                cmd="./my_mpi_program",
                work_path=WRFRUN.config.WRFRUN_TEMP_PATH,
                mpi_use=True,
                mpi_cmd="mpirun",   # the name of MPI run command
                mpi_core_num=core_num
            )

Best Practices
**************

+ Implement both :py:meth:`generate_custom_config <wrfrun.core.base.ExecutableBase.generate_custom_config>` and :py:meth:`load_custom_config <wrfrun.core.base.ExecutableBase.load_custom_config>` for any custom state.
+ Use descriptive names for your executables.
+ Handle errors gracefully in your :py:meth:`before_exec <wrfrun.core.base.ExecutableBase.before_exec>` and :py:meth:`after_exec <wrfrun.core.base.ExecutableBase.after_exec>` methods.
+ Document your executables with docstrings explaining what they do.

For more examples, look at the existing implementations in :doc:`wrf </api/model.wrf.core>` or :doc:`palm </api/model.palm.core>`.
