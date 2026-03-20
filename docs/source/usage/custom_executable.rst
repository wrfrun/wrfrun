Define custom ``Executable``
#############################

This tutorial will teach you how to define a custom ``Executable``. An ``Executable`` is the part of ``wrfrun`` that interacts with external resources (for example, external programs, datasets, etc.). Classes like :class:`GeoGrid <wrfrun.model.wrf.core.GeoGrid>` are examples of ``Executable``.

By defining an ``Executable``, you define how to handle the input, execution, and output of an external program. This allows ``wrfrun`` to precisely control the execution of external programs and also record and replay the execution of the ``Executable`` through the ``replay`` feature.

Background
**********

In ``wrfrun``, all ``Executable`` classes inherit from the same parent class ``ExecutableBase``. When initializing the class, you must provide the following three parameters to the parent class: ``name``, ``cmd``, and ``work_path``.

* ``name``: A string used to uniquely identify this ``Executable`` to ``wrfrun``.
* ``cmd``: A string or a list of strings containing the external command and its parameters to execute.
* ``work_path``: The working path where ``wrfrun`` executes the external command.

In addition, ``ExecutableBase`` accepts three keyword parameters:

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

First, we inherit from the parent class ``ExecutableBase`` and perform the necessary initialization. If you don't know what ``work_path`` should be, you can use the temporary working path defined internally by ``wrfrun``, ``WRFRUN.config.WRFRUN_TEMP_PATH``.

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

The ``add_input_files`` method can accept:
- A single file path string
- A list of file paths
- A dictionary with detailed file configuration
- A list of dictionaries

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

Complete Example
****************

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

            super().before_exec()

        def after_exec(self):
            self.add_output_files(outputs="output.txt")

            super().after_exec()

        def generate_custom_config(self):
            self.custom_config["input_file"] = self.input_file

        def load_custom_config(self):
            self.input_file = self.custom_config["input_file"]

    # Create test files if they don't exist
    if not os.path.exists("test.py"):
        with open("test.py", "w") as f:
            f.write('''with open("input.txt", "r") as f1:
    with open("output.txt", "w") as f2:
        f2.write("Hello from output!\\n")
        f2.write(f1.read())
''')

    if not os.path.exists("input.txt"):
        with open("input.txt", "w") as f:
            f.write("Hello from input!")

    # Use our custom Executable
    with WRFRun("config.toml", init_workspace=True) as wrf_run:
        # Record for replay
        wrf_run.record_simulation(output_path="./outputs/test.replay")
        
        # Create and execute our test executable
        test = Test("input.txt")
        test()

    print("Execution completed! Check the outputs directory.")

Advanced: Using MPI
********************

For programs that require MPI, here's how to set it up:

.. code-block:: python
    :caption: mpi_example.py

    from wrfrun.core import ExecutableBase, WRFRUN

    class MPIProgram(ExecutableBase):
        def __init__(self, core_num: int = 4):
            super().__init__(
                name="mpi_program",
                cmd="./my_mpi_program",  # Must be a string for MPI
                work_path=WRFRUN.config.WRFRUN_TEMP_PATH,
                mpi_use=True,
                mpi_cmd="mpirun",
                mpi_core_num=core_num
            )
            self.class_config["class_args"] = (core_num,)

Best Practices
**************

1. **Always store initialization arguments** in ``self.class_config`` to support replay
2. **Implement both ``generate_custom_config`` and ``load_custom_config``** for any custom state
3. **Use descriptive names** for your executables
4. **Handle errors gracefully** in your ``before_exec`` and ``after_exec`` methods
5. **Document your executables** with docstrings explaining what they do

For more examples, look at the existing implementations in ``wrfrun.model.wrf.core`` or ``wrfrun.model.palm.core``.
