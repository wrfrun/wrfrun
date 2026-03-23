Model Development Guide
#########################

This guide will walk you through the process of modifying an existing model implementation or adding support for a new numerical model to ``wrfrun``. 
Adding a new model involves implementing three main components:

1. **Model Executables** in ``wrfrun/model/[model_name]/`` - Wrappers for each model program
2. **Workspace Management** in ``wrfrun/workspace/[model_name].py`` - Functions to prepare and validate the model workspace
3. **Configuration Template** in ``wrfrun/res/config/[model_name].template.toml`` - Default configuration template

Overview of Model Integration
******************************

All models in ``wrfrun`` follow the same integration pattern to ensure consistency with framework features like record/replay, job scheduling, and progress monitoring. 
The integration process follows these key principles:

- All model executables inherit from :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`
- Workspace preparation is handled by dedicated functions that create symbolic links to model binaries
- Configuration is standardized through TOML templates
- All models provide the same interface to users, regardless of their underlying implementation

Step 1: Create Model Directory Structure
****************************************

First, create the directory structure for your model:

1. **Model implementation directory**: ``wrfrun/model/[model_name]/``
2. **Workspace module**: ``wrfrun/workspace/[model_name].py``
3. **Configuration template**: ``wrfrun/res/config/[model_name].template.toml``

For example, for a new model called "my_model":

.. code-block:: bash

    mkdir wrfrun/model/my_model
    touch wrfrun/model/my_model/__init__.py
    touch wrfrun/model/my_model/core.py
    touch wrfrun/workspace/my_model.py
    touch wrfrun/res/config/my_model.template.toml

Add a ``meson.build`` file in the model directory (refer to existing models for the template).

Step 2: Implement Model Executables
***********************************

The most important part of model integration is implementing the :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` subclasses for each program in your model.

Create a ``core.py`` file in your model directory to implement the executables:

.. code-block:: python
    :caption: wrfrun/model/my_model/core.py

    from wrfrun.core import ExecutableBase, WRFRUN
    from wrfrun.workspace.my_model import get_my_model_workspace_path

    class MyModelProgram(ExecutableBase):
        def __init__(self, custom_param: str = "default"):
            # Initialize with program name, command, and working path
            super().__init__(
                name="my_program",
                cmd="./my_program.exe",
                work_path=get_my_model_workspace_path("main"),
                # Add mpi_use=True and mpi_core_num if program uses MPI
            )

            self.custom_param = custom_param
            
        def before_exec(self):
            # Add input files required by the program
            if not WRFRUN.config.IS_IN_REPLAY:
                self.add_input_files("input.nc")
                self.add_input_files({
                    "file_path": "template.nml",
                    "save_path": self.work_path,
                    "save_name": "namelist.nml",
                    "is_data": False,
                    "is_output": False
                })
            
            super().before_exec()
            
        def after_exec(self):
            # Collect output files produced by the program
            if not WRFRUN.config.IS_IN_REPLAY:
                self.add_output_files(startswith="output_")
                self.add_output_files(endswith=".log")
            
            super().after_exec()
            
        def generate_custom_config(self):
            # Store any custom configuration for replay
            self.custom_config["custom_param"] = self.custom_param
            
        def load_custom_config(self):
            # Load custom configuration during replay
            self.custom_param = self.custom_config["custom_param"]

Implement one :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` subclass for each program in your model (e.g., preprocessor, solver, postprocessor).

Step 3: Create Executable Wrappers
**********************************

To make your executables easy to use, create wrapper functions in ``core.py``:

.. code-block:: python
    :caption: wrfrun/model/my_model/core.py

    # Add this at the bottom of core.py
    def my_program(custom_param: str = "default"):
        """
        Run my_program executable.
        
        :param custom_param: Custom parameter for the program
        :type custom_param: str
        """
        MyModelProgram(custom_param=custom_param)()

Then export these functions in your model's ``__init__.py``:

.. code-block:: python
    :caption: wrfrun/model/my_model/__init__.py

    """
    wrfrun.model.my_model
    #####################
    Implementation of MyModel.
    """

    from .core import *

And also add the export to the top-level model ``__init__.py`` if needed.

Step 4: Implement Workspace Management
***************************************

Create the workspace module to prepare the model's working directory:

.. code-block:: python
    :caption: wrfrun/workspace/my_model.py

    from os import listdir, makedirs, symlink
    from os.path import exists
    from wrfrun.core import WRFRUN, WRFRunConfig
    from wrfrun.log import logger
    from wrfrun.utils import check_path

    # Global variables to store workspace paths
    # Change `MAIN` to your models name
    WORKSPACE_MODEL_MAIN = ""

    def _register_my_model_workspace_uri(wrfrun_config: WRFRunConfig):
        """
        Hook to initialize workspace paths when config loads.
        """
        global WORKSPACE_MODEL_MAIN
        WORKSPACE_MODEL_MAIN = f"{wrfrun_config.WRFRUN_WORKSPACE_MODEL}/MY_MODEL"

    # Register the hook to be called when config initializes
    WRFRUN.set_config_register_func(_register_my_model_workspace_uri)

    def get_my_model_workspace_path(name: str = "main") -> str:
        """
        Get workspace path for MyModel components.
        """
        return WORKSPACE_MODEL_MAIN

    def prepare_my_model_workspace(model_config: dict):
        """
        Prepare workspace for MyModel by linking binaries and required files.
        
        :param model_config: Model configuration from TOML file
        :type model_config: dict
        """
        logger.info("Initialize workspace for MyModel.")
        
        model_path = model_config["model_path"]
        if not model_path or not exists(model_path):
            logger.error("MyModel installation path not found in configuration.")
            raise FileNotFoundError("Invalid MyModel path in configuration.")
        
        # Create workspace directory
        work_path = WRFRUN.config.parse_resource_uri(WORKSPACE_MODEL_MAIN)
        check_path(work_path, force=True)
        
        # Link all required binaries from the model installation
        binaries = ["my_program.exe", "preprocess.exe", "postprocess.exe"]
        for binary in binaries:
            src_path = f"{model_path}/bin/{binary}"
            if exists(src_path):
                symlink(src_path, f"{work_path}/{binary}")
            else:
                logger.warning(f"Binary {binary} not found in model installation.")

    def check_my_model_workspace(model_config: dict) -> bool:
        """
        Check if MyModel workspace is properly set up.
        
        :param model_config: Model configuration
        :type model_config: dict
        :return: True if workspace is valid, False otherwise
        :rtype: bool
        """
        work_path = WRFRUN.config.parse_resource_uri(WORKSPACE_MODEL_MAIN)
        return exists(work_path)

    __all__ = ["get_my_model_workspace_path", "prepare_my_model_workspace", "check_my_model_workspace"]

Register your workspace functions in ``wrfrun/workspace/core.py``:

.. code-block:: python
    :caption: wrfrun/workspace/core.py

    # Add imports
    from .my_model import prepare_my_model_workspace, check_my_model_workspace

    # Add to function maps
    PREPARE_FUNC_MAP = {"wrf": prepare_wrf_workspace, "palm": prepare_palm_workspace, "my_model": prepare_my_model_workspace}
    CHECK_FUNC_MAP = {"wrf": check_wrf_workspace, "my_model": check_my_model_workspace}

Step 5: Create Configuration Template
*************************************

Create a TOML configuration template for your model in ``wrfrun/res/config/``:

.. important::
    After adding your template file, you must update ``wrfrun/res/config/name_map.json`` to add an entry for your new template. 
    This allows the resource system to generate a constant for your template.
    For more information about the resource system and name_map.json, see :doc:`develop_guide_res`.

.. code-block:: toml
    :caption: wrfrun/res/config/my_model.template.toml

    # MyModel configuration template
    model_path = "/path/to/your/mymodel/installation"
    
    # Simulation settings
    simulation_type = "default"
    debug_level = 100
    
    [domain]
    domain_num = 1
    dx = 1000.0
    dy = 1000.0
    nx = 100
    ny = 100
    
    [time]
    start_date = 2023-01-01T00:00:00Z
    end_date = 2023-01-02T00:00:00Z
    time_step = 60.0
    
    [physics]
    radiation_scheme = "rrtmg"
    boundary_layer_scheme = "ysu"

Add the template to ``wrfrun/res/config/meson.build`` so it gets installed.

Step 6: Update Main Configuration Template
******************************************

Add your model to the main configuration template in ``wrfrun/res/config/config.template.toml``:

.. code-block:: toml
    :caption: wrfrun/res/config/config.template.toml

    [model]
    # ... existing models ...
    
    [model.my_model]
    # If you want to use MyModel, set use to true
    use = false
    # Import MyModel configuration from separate file
    include = "./configs/my_model.toml"

Step 7: Test Your Implementation
********************************

1. Create a test configuration that enables your model
2. Verify the workspace is prepared correctly
3. Test running your model executables
4. Verify record/replay functionality works
5. Test job submission if applicable (Optional)

Modifying an Existing Model
***************************

If you're modifying an existing model instead of adding a new one:

1. **Modifying Executables**: Edit the corresponding files in ``wrfrun/model/[model_name]/``
2. **Changing Workspace Behavior**: Edit ``wrfrun/workspace/[model_name].py``
3. **Updating Configuration**: Update the template in ``wrfrun/res/config/[model_name].template.toml``
4. **Maintain backward compatibility**: Don't break existing user code when making changes

Best Practices
**************

1. **Follow the Executable contract**: Always implement ``generate_custom_config()`` and ``load_custom_config()`` for record/replay support
2. **Use relative paths**: Work with paths relative to the workspace directory
3. **Handle errors properly**: Raise descriptive exceptions for common error cases
4. **Add logging**: Use the logger to provide useful information about the execution process
5. **Document your model**: Add docstrings to all public functions and classes
6. **Follow naming conventions**: Use lowercase with underscores for module and function names, PascalCase for classes
7. **Test on multiple environments**: Ensure your implementation works on different systems and cluster environments

Next Steps
**********

- For core module development, see :doc:`develop_guide_core`
- For style guidelines, see :doc:`coding_style`
- For API reference, see the :doc:`/api/model` section
