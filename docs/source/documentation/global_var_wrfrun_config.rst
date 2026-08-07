Property ``WRFRUN.config``
##########################

The :py:meth:`config <wrfrun.core.core.WRFRUNProxy.config>` property holds the
active :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` instance. It
loads the TOML configuration, manages namelists and debug settings, and tracks
the current ``wrfrun`` context. URI names and URI-to-path resolution belong to
the separate :py:meth:`WRFRUN.uri <wrfrun.core.core.WRFRUNProxy.uri>` manager.

Class Architecture
******************

``WRFRunConfig`` inherits two mixins:

- :class:`NamelistMixIn <wrfrun.core._namelist.NamelistMixIn>` manages
  registered Fortran namelists.
- :class:`DebugMixIn <wrfrun.core._debug.DebugMixIn>` provides debug-mode
  settings.

The associated :class:`WRFRUNURI <wrfrun.core.uri.WRFRUNURI>` instance is not
a ``WRFRunConfig`` mixin. It owns URI registration and resolution and exposes
standard URI names such as ``WRFRUN_TEMP_PATH``, ``WRFRUN_WORKSPACE_ROOT``,
``WRFRUN_WORKSPACE_MODEL``, ``WRFRUN_WORKSPACE_REPLAY``,
``WRFRUN_OUTPUT_PATH``, and ``WRFRUN_RESOURCE_PATH`` through ``WRFRUN.uri``.

``WRFRunConfig`` also stores the configuration dictionary and framework state,
including ``IS_IN_REPLAY``, ``IS_RECORDING``, ``FAKE_SIMULATION_MODE``, and
``WRFRUN_WORK_STATUS``. Use ``check_wrfrun_context()`` when code requires an
active :class:`WRFRun <wrfrun.run.WRFRun>` context.

Working with URIs
*****************

Use ``WRFRUN.uri`` for all new URI operations. A URI begins with
``:WRFRUN_`` and ends with ``:``; resolve it before passing it to a filesystem
API.

.. code-block:: python
    :caption: Using resource URIs

    from wrfrun.core import WRFRUN

    temp_file_uri = f"{WRFRUN.uri.WRFRUN_TEMP_PATH}/test.txt"
    temp_file = WRFRUN.uri.parse_resource_uri(temp_file_uri)

    custom_uri = ":WRFRUN_MY_DATA:"
    if not WRFRUN.uri.check_resource_uri(custom_uri):
        WRFRUN.uri.register_resource_uri(custom_uri, "/path/to/my/data")

``WRFRUN.config`` still forwards ``check_resource_uri()``,
``register_resource_uri()``, ``unregister_resource_uri()``, and
``parse_resource_uri()`` to the URI manager for backward compatibility. New
code and documentation should call ``WRFRUN.uri`` directly.

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

Beyond its mixins, :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` provides the following core configuration management features:

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

    # Resolve a standard URI.
    temp_dir = WRFRUN.uri.parse_resource_uri(WRFRUN.uri.WRFRUN_TEMP_PATH)

    # Use a URI in a path.
    namelist_path = WRFRUN.uri.parse_resource_uri(
        f"{WRFRUN.uri.WRFRUN_TEMP_PATH}/namelist.wps"
    )

    # Register and resolve a custom URI.
    WRFRUN.uri.register_resource_uri(":WRFRUN_MY_PROJECT:", "/home/user/my_project")
    my_data_path = WRFRUN.uri.parse_resource_uri(":WRFRUN_MY_PROJECT:/data/input.nc")

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
+ **Initialize before access**: Construct :class:`WRFRun <wrfrun.run.WRFRun>` before accessing ``WRFRUN.config`` or ``WRFRUN.uri``. Operations that require an active simulation context should call ``check_wrfrun_context(True)``.
+ **Prefer convenience methods**: Use the dedicated accessor methods (:py:meth:`get_model_config <wrfrun.core._config.WRFRunConfig.get_model_config>`, :py:meth:`get_log_path <wrfrun.core._config.WRFRunConfig.get_log_path>`, etc.) instead of direct dictionary access for better type safety and error handling.
+ **Make deliberate runtime updates**: ``update_model_config()`` and namelist updates are supported. Keep such changes explicit so that the effective configuration remains understandable and reproducible.
+ **Use URIs for path management**: Always use resource URIs instead of hard-coded paths to ensure your code is portable across different environments.
+ **Save configuration snapshots**: Always save a copy of your configuration with your simulation outputs to ensure full reproducibility of results.
+ **Use environment variables for debug mode**: Set debug mode via environment variables during development to avoid modifying code to enable/disable debugging.
