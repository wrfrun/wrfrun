Property ``WRFRUN.config``
##########################

The :py:meth:`config <wrfrun.core.core.WRFRUNProxy.config>` property holds an instance of :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`, 
which is the core configuration management class in ``wrfrun``, designed as a composite class that inherits from four specialized mixin classes to provide a complete, 
all-in-one configuration solution for the entire framework. 
It centralizes all configuration-related functionality, eliminating the need to manage separate configuration systems for different components.

Class Architecture
******************

:class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` uses multiple inheritance to combine functionality from four mixin classes, each responsible for a specific aspect of configuration management:

.. inheritance-diagram:: wrfrun.core._config.WRFRunConfig
    :parts: 1

+ :class:`ConstantMixIn <wrfrun.core._constant.ConstantMixIn>`: Manages runtime constants, standard paths, and global state
+ :class:`ResourceMixIn <wrfrun.core._resource.ResourceMixIn>`: Handles resource URI registration and path resolution
+ :class:`NamelistMixIn <wrfrun.core._namelist.NamelistMixIn>`: Manages Fortran namelist files for numerical models
+ :class:`DebugMixIn <wrfrun.core._debug.DebugMixIn>`: Provides debug mode controls and logging configuration

This modular design allows for separation of concerns while providing a unified interface to all configuration functionality through a single class instance.

Mixin Class Functionality
*************************

ConstantMixIn
=============

The :class:`ConstantMixIn <wrfrun.core._constant.ConstantMixIn>` provides management of runtime constants, standard directory paths, and global framework state:

+ **Standard Path Management**: Defines and manages standard directory paths used throughout the framework:
   - ``WRFRUN_HOME_PATH``: Root directory for wrfrun configuration and data
   - ``WRFRUN_TEMP_PATH``: Temporary working directory for model runs
   - ``WRFRUN_WORKSPACE_ROOT``: Root directory for all workspaces
   - ``WRFRUN_WORKSPACE_MODEL``: Directory for model execution
   - ``WRFRUN_WORKSPACE_REPLAY``: Directory for simulation replay files
   - ``WRFRUN_OUTPUT_PATH``: Output directory for simulation results
   - ``WRFRUN_RESOURCE_PATH``: Directory for built-in resource files
+ **Global State Management**: Tracks global framework state:
   - ``IS_IN_REPLAY``: Flag indicating if a simulation replay is in progress
   - ``IS_RECORDING``: Flag indicating if simulation recording is active
   - ``FAKE_SIMULATION_MODE``: Flag for dry-run mode where models are not actually executed
   - ``WRFRUN_CONTEXT_STATUS``: Tracks whether we are inside a :class:`WRFRun <wrfrun.run.WRFRun>` context
   - ``WRFRUN_WORK_STATUS``: Tracks the current execution step for progress reporting
+ **Context Validation**: Provides methods to check if the code is running within a valid :class:`WRFRun <wrfrun.run.WRFRun>` context, preventing incorrect usage of framework components.

ResourceMixIn
=============

The :class:`ResourceMixIn <wrfrun.core._resource.ResourceMixIn>` implements a URI-based resource management system that ensures code portability across different environments:

- **URI Registration**: Allows registering custom resource URIs that map to physical file paths. URIs follow the format ``:WRFRUN_*:`` (e.g., ``:WRFRUN_TEMP_PATH:``).
- **URI Resolution**: Automatically resolves URIs to their corresponding physical paths at runtime.
- **Portability**: Enables the same code to run on different machines without modification, as URIs are resolved based on the local environment configuration.
- **Built-in URIs**: Provides pre-registered URIs for all standard framework paths.

.. code-block:: python
    :caption: Using resource URIs

    from wrfrun.core import WRFRUN

    # Resolve a URI to an absolute path
    temp_file = WRFRUN.config.parse_resource_uri(":WRFRUN_TEMP_PATH:/test.txt")
    
    # Register a custom URI
    WRFRUN.config.register_resource_uri(":WRFRUN_MY_DATA:", "/path/to/my/data")

NamelistMixIn
=============

The :class:`NamelistMixIn <wrfrun.core._namelist.NamelistMixIn>` provides comprehensive management of Fortran namelist files, 
which are commonly used by numerical weather prediction models:

- **Namelist Registration**: Supports registering multiple namelist configurations with unique IDs (e.g., "wps", "wrf", "palm").
- **Reading and Writing**: Can read existing namelist files and generate new ones from configuration values.
- **Update Management**: Allows partial updates to namelist values without modifying the entire file.
- **Validation**: Ensures namelist IDs are properly registered before use, preventing errors.
- **Built-in Support**: Includes pre-registered support for common model namelists (WPS, WRF, WRFDA, PALM).

.. code-block:: python
    :caption: Working with namelists

    from wrfrun.core import WRFRUN

    # Update WPS namelist values
    WRFRUN.config.update_namelist({
        "share": {
            "max_dom": 2,
            "start_date": ["2023-01-01_00:00:00", "2023-01-01_00:00:00"],
            "end_date": ["2023-01-02_00:00:00", "2023-01-02_00:00:00"]
        }
    }, namelist_id="wps")
    
    # Write the complete namelist to a file
    WRFRUN.config.write_namelist(":WRFRUN_TEMP_PATH:/namelist.wps", "wps")

DebugMixIn
==========

The :class:`DebugMixIn <wrfrun.core._debug.DebugMixIn>` provides debug configuration and logging controls:

+ **Granular Debug Controls**: Separate debug switches for different components:
   - ``DEBUG_MODE``: Global debug mode switch
   - ``DEBUG_MODE_LOGGER``: Controls debug logging output
   - ``DEBUG_MODE_EXECUTABLE``: Controls debug output for executable execution
+ **Environment Variable Support**: Debug modes can be set via environment variables for easy configuration without code changes:
   - ``WRFRUN_DEBUG_MODE``: Global debug mode
   - ``WRFRUN_DEBUG_MODE_LOGGER``: Logger debug mode
   - ``WRFRUN_DEBUG_MODE_EXECUTABLE``: Executable debug mode
+ **Automatic Log Level Adjustment**: Automatically adjusts the logging level based on debug mode settings.

.. code-block:: python
    :caption: Enabling debug mode

    from wrfrun.core import WRFRUN

    # Enable global debug mode
    WRFRUN.config.DEBUG_MODE = True
    
    # Enable detailed executable debugging
    WRFRUN.config.DEBUG_MODE_EXECUTABLE = True

Core WRFRunConfig Functionality
*******************************

Beyond the functionality inherited from mixins, :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` provides the following core configuration management features:

Configuration Loading
=====================

- **TOML Support**: Reads configuration from TOML format files, providing a human-readable and easy-to-edit configuration format.
- **Modular Configuration**: Supports splitting configuration into multiple files, with model-specific configurations loaded from separate files via the ``include`` directive.
- **Automatic Merging**: Automatically merges main configuration with model-specific configuration files.
- **Path Resolution**: Resolves all relative paths in configuration files relative to the main configuration file location.
- **Template Generation**: Automatically copies the default configuration template to the specified path if the configuration file does not exist.
- **Validation**: Performs basic validation of configuration values during loading.

Configuration Access
====================

- **Dictionary-style Access**: Allows accessing configuration values using square bracket notation, similar to Python dictionaries.
- **Deep Copy Semantics**: Returns deep copies of configuration values to prevent accidental modification of internal state.
- **Convenience Accessors**: Provides dedicated methods for commonly accessed configuration values

Configuration Management
========================

- **Runtime Updates**: Allows updating configuration values at runtime with proper validation.
- **Model Configuration Updates**: Provides a dedicated method for safely updating model-specific configurations.
- **Configuration Saving**: Can save the current complete configuration to a TOML file for reproducibility.
- **Snapshot Generation**: Automatically saves a copy of the configuration to the output directory when a simulation starts.

Usage Examples
**************

Basic Configuration Access
==========================

.. code-block:: python

    from wrfrun.core import WRFRUN
    from wrfrun.run import WRFRun

    with WRFRun("config.toml") as wrf_run:
        # Access top-level configuration
        core_count = WRFRUN.config.get_core_num()
        output_path = WRFRUN.config["output_path"]
        
        # Get model configuration
        wrf_config = WRFRUN.config.get_model_config("wrf")
        wps_path = wrf_config["wps_path"]
        geog_data_path = wrf_config["geog_data_path"]
        
        # Use convenience methods
        log_path = WRFRUN.config.get_log_path()
        server_host, server_port = WRFRUN.config.get_socket_server_config()

Working with URIs
=================

.. code-block:: python

    # Resolve a standard URI
    temp_dir = WRFRUN.config.parse_resource_uri(WRFRUN.config.WRFRUN_TEMP_PATH)
    
    # Use URIs in file paths
    namelist_path = WRFRUN.config.parse_resource_uri(f"{WRFRUN.config.WRFRUN_TEMP_PATH}/namelist.wps")
    
    # Register a custom URI
    WRFRUN.config.register_resource_uri(":WRFRUN_MY_PROJECT:", "/home/user/my_project")
    my_data_path = WRFRUN.config.parse_resource_uri(":WRFRUN_MY_PROJECT:/data/input.nc")

Modifying Namelists
===================

.. code-block:: python

    # Update multiple namelist values
    WRFRUN.config.update_namelist({
        "domains": {
            "e_we": [100, 200],
            "e_sn": [100, 200],
            "dx": [27000, 9000],
            "dy": [27000, 9000]
        },
        "physics": {
            "mp_physics": 8,
            "ra_lw_physics": 4,
            "ra_sw_physics": 4
        }
    }, namelist_id="wrf")
    
    # Write the updated namelist
    WRFRUN.config.write_namelist(":WRFRUN_TEMP_PATH:/namelist.input", "wrf")

Enabling Debug Mode
===================

.. code-block:: python

    # Enable debug logging only
    WRFRUN.config.DEBUG_MODE_LOGGER = True
    
    # Enable full debug mode for development
    WRFRUN.config.DEBUG_MODE = True

Best Practices
**************

+ **Access through WRFRUN proxy**: Always access the configuration through ``WRFRUN.config`` rather than creating your own :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` instances. The framework manages the configuration lifecycle automatically.
+ **Use within WRFRun context**: Never access ``WRFRUN.config`` outside of a :class:`WRFRun <wrfrun.run.WRFRun>` context, as it will not be fully initialized yet and may cause errors.
+ **Prefer convenience methods**: Use the dedicated accessor methods (:py:meth:`get_model_config <wrfrun.core._config.WRFRunConfig.get_model_config>`, :py:meth:`get_log_path <wrfrun.core._config.WRFRunConfig.get_log_path>`, etc.) instead of direct dictionary access for better type safety and error handling.
+ **Avoid runtime modifications**: The configuration is designed to be immutable once loaded. Avoid modifying values at runtime unless absolutely necessary, as it may lead to unexpected behavior.
+ **Use URIs for path management**: Always use resource URIs instead of hard-coded paths to ensure your code is portable across different environments.
+ **Save configuration snapshots**: Always save a copy of your configuration with your simulation outputs to ensure full reproducibility of results.
+ **Use environment variables for debug mode**: Set debug mode via environment variables during development to avoid modifying code to enable/disable debugging.
