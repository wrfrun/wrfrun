Global Variable ``WRFRUN``
##########################

:py:data:`WRFRUN <wrfrun.core.core.WRFRUN>` is a global singleton proxy instance, 
which provides unified access to core framework components across all modules in ``wrfrun``. 
It acts as a central registry and access point for configuration, executable registry, and simulation recording functionality.

Overview
********

:py:data:`WRFRUN <wrfrun.core.core.WRFRUN>` is an instance of :class:`WRFRUNProxy <wrfrun.core.core.WRFRUNProxy>` that is initialized once when the package is imported. 
It eliminates the need to pass core objects between functions and modules, making the API cleaner and easier to use.

It manages three core components:

- **Configuration**: Global runtime configuration loaded from your TOML file
- **Executable Database**: Registry of all available :class:`Executable <wrfrun.core.base.ExecutableBase>` implementations
- **Simulation Recorder**: Handles recording and replaying of simulation runs

Core Components
***************

``WRFRUN.config``
=================

The :py:meth:`config <wrfrun.core.core.WRFRUNProxy.config>` property provides access to the global :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` instance, which contains all runtime settings loaded from your configuration file.

.. code-block:: python
    :caption: Accessing configuration values

    from wrfrun.core import WRFRUN

    # Get workspace paths
    output_path = WRFRUN.config.WRFRUN_OUTPUT_PATH
    temp_path = WRFRUN.config.WRFRUN_TEMP_PATH

    # Get model configuration
    wrf_config = WRFRUN.config.get_model_config("wrf")
    core_count = WRFRUN.config["core_num"]

    # Save a copy of the current configuration
    WRFRUN.config.save_wrfrun_config("./saved_config.toml")

``WRFRUN.ExecDB``
=================

The :py:meth:`ExecDB <wrfrun.core.core.WRFRUNProxy.ExecDB>` property provides access to the :class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>` instance, which is the central registry of all available executable implementations in the framework.

.. code-block:: python
    :caption: Working with the executable database

    from wrfrun.core import WRFRUN

    # Get an executable class by name
    geogrid_class = WRFRUN.ExecDB.get_cls("geogrid")

    # Register a custom executable
    from my_custom_exec import MyExecutable
    WRFRUN.ExecDB.register_exec("my_exec", MyExecutable)

``WRFRUN.record``
=================

The :py:meth:`record <wrfrun.core.core.WRFRUNProxy.record>` property provides access to the :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>` instance, which handles recording of simulation runs for later replay. 
This component is only initialized when you call :py:meth:`record_simulation <wrfrun.run.WRFRun.record_simulation>` on the :class:`WRFRun <wrfrun.run.WRFRun>` context manager.

.. code-block:: python
    :caption: Using the simulation recorder

    from wrfrun.run import WRFRun

    with WRFRun("config.toml") as wrf_run:
        wrf_run.record_simulation("./my_simulation.replay")

        # ... run simulation steps

Initialization Flow
*******************

The three components are initialized at different stages:

+ **Executable Database**: Initialized automatically when the package is imported. It automatically registers all built-in executables.
+ **Configuration**: Initialized when you create a :class:`WRFRun <wrfrun.run.WRFRun>` context manager, loading settings from your configuration file.
+ **Simulation Recorder**: Initialized explicitly when you call :py:meth:`record_simulation <wrfrun.run.WRFRun.record_simulation>` within a :class:`WRFRun <wrfrun.run.WRFRun>` context.

You can check if a component is initialized using the :py:meth:`is_initialized <wrfrun.core.core.WRFRUNProxy.is_initialized>` method:

.. code-block:: python

    from wrfrun.core import WRFRUN

    # Check if config is initialized
    if WRFRUN.is_initialized("config"):
        print("Configuration is loaded")

    # Check if recorder is available
    if WRFRUN.is_initialized("record"):
        print("Recording is active")

    # Check if ExecDB is available
    if WRFRUN.is_initialized("exec_db"):
        print("ExecDB is initialized")

Advanced Features
*****************

Registering Configuration Callbacks
===================================

You can register callback functions that will be executed when the configuration is initialized. 
This is particularly useful for extension developers who need to perform setup based on configuration values.

.. code-block:: python

    from wrfrun.core import WRFRUN

    def my_config_callback(config):
        # This function will be called when config is initialized
        print(f"Output path set to: {config.WRFRUN_OUTPUT_PATH}")

    WRFRUN.set_config_register_func(my_config_callback)

If the configuration is already initialized when you register the callback, it will be executed immediately. 
Otherwise, it will be stored and executed once the configuration is loaded.

Registering Executable Database Callbacks
=========================================

Similarly, you can register callbacks to be executed when the executable database is initialized:

.. code-block:: python

    from wrfrun.core import WRFRUN

    def my_execdb_callback(exec_db):
        # Register custom executable when ExecDB is initialized
        from my_extension import MyCustomExec
        exec_db.register_executable(MyCustomExec)

    WRFRUN.set_exec_db_register_func(my_execdb_callback)

Best Practices
**************

+ **Use within WRFRun context only**: Always access ``WRFRUN.config`` and ``WRFRUN.record`` from within a :class:`WRFRun <wrfrun.run.WRFRun>` context manager. Accessing them outside the context may raise a :class:`ConfigError <wrfrun.core.error.ConfigError>`.
+ **Avoid modifying configuration at runtime**: The configuration is designed to be immutable once loaded. Modifying it during runtime may lead to unexpected behavior.
+ **Use callbacks for extensions**: If you are developing an extension, always use the callback registration methods instead of trying to access components directly at import time.
+ **Don't store references**: Avoid storing references to ``WRFRUN.config``, ``WRFRUN.ExecDB``, or ``WRFRUN.record`` in long-lived objects. Always access them through the global ``WRFRUN`` instance to ensure you get the current active instance.

.. toctree::
   :maxdepth: 1
   :caption: Documentation
   :hidden:

   global_var_wrfrun_config
