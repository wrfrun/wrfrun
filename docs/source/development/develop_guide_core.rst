wrfrun.core Module Development Guide
####################################

The ``wrfrun.core`` module is the foundation of the entire ``wrfrun`` framework, providing all core abstractions, base classes, and common functionality used throughout the project. 
This guide will help you understand its architecture and how to work with it effectively.

Module Overview
***************

The core module is designed to be modular and extensible, with clear separation of concerns. 
It consists of several key components:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Component
      - Responsibility
    * - :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`
      - Base class for all external program wrappers
    * - :class:`WRFRUN <wrfrun.core.core.WRFRUN>`
      - Global singleton proxy for accessing core services
    * - :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>`
      - Unified configuration management system
    * - :class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>`
      - Registry for all available Executable classes
    * - :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>`
      - Simulation recording functionality
    * - Namelist management
      - Fortran namelist parsing and generation
    * - Resource management
      - URI-based resource path resolution
    * - Type definitions
      - Common type definitions and TypedDicts
    * - Error hierarchy
      - Custom exception classes for all error scenarios
    * - Socket server
      - Real-time simulation progress monitoring

Core Architecture
*****************

The core module follows a layered architecture:

1. **Abstraction Layer**: Defines base classes and interfaces (e.g., :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`)
2. **Service Layer**: Provides core services like configuration, registry, and recording
3. **Utility Layer**: Common utilities for subprocess execution, file handling, etc.

This design allows for maximum flexibility and extensibility while maintaining consistency across the entire codebase.

Key Components Deep Dive
************************

ExecutableBase
==============

:class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` is the most important class in the core module. 
All wrappers for external programs (like WPS, WRF, PALM, etc.) inherit from this base class. 
It provides a standardized interface for executing external programs, managing inputs/outputs, and supporting the record/replay feature.

Lifecycle of an Executable
--------------------------
When you call an Executable instance (e.g., :py:func:`geogrid <wrfrun.model.wrf.exec_wrap.geogrid>`), it follows this lifecycle:

1. ``before_exec()``: Prepares input files by linking them to the working directory
2. ``exec()``: Executes the external command
3. ``after_exec()``: Collects and saves output files to the output directory

These three methods are called automatically by ``__call__()``. You can override any of them in your subclass to add custom behavior.

Core Methods to Implement
-------------------------
When creating a new Executable, you need to implement/override these methods:

1. ``__init__()``: Initialize the executable with its name, command, and working path
2. ``before_exec()``: (Optional) Add custom input preparation logic
3. ``after_exec()``: (Optional) Add custom output collection logic
4. ``generate_custom_config()``: Required for record/replay support - stores any custom configuration
5. ``load_custom_config()``: Required for record/replay support - loads custom configuration during replay

Example Executable Implementation
---------------------------------
Here's a minimal example of a custom Executable:

.. code-block:: python

    from wrfrun.core import ExecutableBase, WRFRUN

    class MyProgram(ExecutableBase):
        def __init__(self, custom_param: str = "default"):
            super().__init__(
                name="my_program",
                cmd="./my_program",
                work_path=WRFRUN.config.WRFRUN_TEMP_PATH
            )

            self.custom_param = custom_param
            
        def before_exec(self):

            if not WRFRUN.config.IS_IN_REPLAY
                # Don't have to add again when replaying simulation
                # Add required input files
                self.add_input_files("input.dat")

            super().before_exec()
            
        def after_exec(self):
            if not WRFRUN.config.IS_IN_REPLAY
                # Don't have to add again when replaying simulation
                # Collect output files
                self.add_output_files(endswith=".out")

            super().after_exec()
            
        def generate_custom_config(self):
            self.custom_config["custom_param"] = self.custom_param
            
        def load_custom_config(self):
            self.custom_param = self.custom_config["custom_param"]

Type System
===========

The ``wrfrun.core.type`` module defines common TypedDicts and enumerations used throughout the framework:

- :class:`FileConfigDict <wrfrun.core.type.FileConfigDict>`: Structure for describing input/output files
- :class:`ExecutableConfig <wrfrun.core.type.ExecutableConfig>`: Complete configuration for an Executable
- :class:`InputFileType <wrfrun.core.type.InputFileType>`: Enum for distinguishing between built-in and custom resources

Using these types ensures type safety and consistency across all components.

Error Hierarchy
===============

All exceptions in ``wrfrun`` inherit from :class:`WRFRunBasicError <wrfrun.core.error.WRFRunBasicError>`, allowing you to catch all wrfrun-specific exceptions if needed. Key exception types include:

- :class:`ConfigError <wrfrun.core.error.ConfigError>`: Configuration-related errors
- :class:`WRFRunContextError <wrfrun.core.error.WRFRunContextError>`: Operation attempted outside of WRFRun context
- :class:`CommandError <wrfrun.core.error.CommandError>`: External command execution failed
- :class:`OutputFileError <wrfrun.core.error.OutputFileError>`: Expected output files not found
- :class:`ModelNameError <wrfrun.core.error.ModelNameError>`: Requested model not found in configuration

Always use the appropriate exception type when raising errors in your code.

Global Singleton WRFRUN
=======================

The :data:`WRFRUN <wrfrun.core.core.WRFRUN>` global singleton provides unified access to all core services:

- ``WRFRUN.config``: Access to the global configuration
- ``WRFRUN.ExecDB``: Access to the Executable registry
- ``WRFRUN.record``: Access to the simulation recorder (when recording is active)

You should always use this singleton instead of creating instances of these services yourself. 
For more details, see :doc:`/documentation/global_var_wrfrun`.

Other Core Components
=====================

ExecutableDB
------------
:class:`ExecutableDB <wrfrun.core._exec_db.ExecutableDB>` is the registry for all Executable classes. 
All Executables are automatically registered when their module is imported. 
You can use it to dynamically look up Executable classes by name:

.. code-block:: python

    from wrfrun.core import WRFRUN
    exec_class = WRFRUN.ExecDB.get_cls("geogrid")
    exec_instance = exec_class()

Namelist Management
-------------------
The :class:`NamelistMixIn <wrfrun.core._namelist.NamelistMixIn>` provides functionality for reading, modifying, 
and writing Fortran namelist files, which are commonly used by numerical weather prediction models.

Resource Management
-------------------
The :class:`ResourceMixIn <wrfrun.core._resource.ResourceMixIn>` implements the URI-based resource system that allows code to be environment-agnostic.

Simulation Recording and Replay
-------------------------------
The :class:`ExecutableRecorder <wrfrun.core._record.ExecutableRecorder>` and replay functionality allow simulations to be recorded and reproduced exactly on any machine.

Socket Server
-------------
The socket server provides real-time progress monitoring capabilities for running simulations.

Extending the Core Module
*************************

When to Extend Core
===================
You should consider extending the core module when:

1. You need to add new base functionality that will be used across multiple models
2. You need to modify the behavior of core services
3. You are adding a new core feature that benefits all users

When to Build on Top of Core
============================
For most use cases, you should build on top of the core module rather than modifying it:

1. Adding support for a new numerical model
2. Creating custom preprocessing or postprocessing steps
3. Building extensions for specific use cases

Best Practices for Core Development
***********************************

1. **Maintain backward compatibility**: Never break existing public APIs. If changes are needed, deprecate old APIs first.
2. **Follow the interface contract**: All Executables must adhere to the :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` interface to ensure compatibility with record/replay and other features.
3. **Add comprehensive type hints**: All public APIs must have full type annotations.
4. **Write proper docstrings**: Use Sphinx-style docstrings for all public classes and methods.
5. **Handle errors properly**: Always raise appropriate exceptions with descriptive messages.
6. **Test thoroughly**: Core functionality should have high test coverage.
7. **Keep core generic**: Avoid adding model-specific logic to the core module.

Next Steps
**********

- To learn how to add a new model, see :doc:`develop_guide_model`
- For API reference, see the :doc:`/api/core` section
- For more about the global configuration system, see :doc:`/documentation/global_var_wrfrun_config`
