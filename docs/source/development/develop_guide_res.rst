Resource Module Development Guide
#################################

The :doc:`wrfrun.res </api/res>` module contains all static resources used by the ``wrfrun`` framework, 
including configuration templates, job scheduler templates, namelist templates, scripts, and other shared files. 
This guide explains how the resource system works and how to add or modify resources.

Module Overview
***************

The resource system is designed to:

- Centralize all static files in one location
- Provide type-safe access to resources through auto-generated constants
- Automatically register resource URIs for cross-environment compatibility
- Simplify resource management across the framework

All resources are accessed through auto-generated constants in :doc:`wrfrun.res </api/res>`, 
eliminating hardcoded file paths throughout the codebase.

Directory Structure
*******************

The ``wrfrun/res/`` directory is organized by resource type:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Directory
      - Contents
    * - ``config/``
      - TOML configuration templates for all supported models and the main configuration
    * - ``extension/``
      - Resources for framework extensions (e.g., NCL scripts, data files)
    * - ``namelist/``
      - Fortran namelist templates for numerical models
    * - ``scheduler/``
      - Job submission script templates for PBS, Slurm, and LSF schedulers
    * - Root files
      - Run script templates, gitignore rules, and other shared resources

Each directory contains a ``name_map.json`` file that describes the resources in that directory.

Understanding name_map.json
***************************

Every directory in the resource hierarchy must contain a ``name_map.json`` file that maps physical file/directory names to their corresponding constant names used in the code.

File Format
===========
Each entry in ``name_map.json`` has this structure:

.. code-block:: json

    {
        "physical_file_name": {
            "name": "CONSTANT_NAME",
            "type": "file" | "dir"
        }
    }

- ``physical_file_name``: The actual name of the file or directory on disk
- ``name``: The name to use for the auto-generated constant (UPPER_SNAKE_CASE)
- ``type``: Either "file" for regular files or "dir" for directories

Example
=======

For the root ``name_map.json``:

.. code-block:: json
    :caption: wrfrun/res/name_map.json

    {
        "config": {
            "name": "CONFIG",
            "type": "dir"
        },
        "run.template.sh": {
            "name": "RUN_SH_TEMPLATE",
            "type": "file"
        }
    }

For the config directory's ``name_map.json``:

.. code-block:: json
    :caption: wrfrun/res/config/name_map.json

    {
        "config.template.toml": {
            "name": "MAIN_TOML_TEMPLATE",
            "type": "file"
        },
        "wrf.template.toml": {
            "name": "WRF_TOML_TEMPLATE",
            "type": "file"
        }
    }

These will generate constants like ``CONFIG_MAIN_TOML_TEMPLATE`` and ``RUN_SH_TEMPLATE``.

generate_init.py Script
************************

The ``generate_init.py`` script automatically generates the ``__init__.py`` file for the resource module based on the ``name_map.json`` files. 
This script runs automatically during the build process.

How It Works
============
1. **Recursive Scanning**: The script recursively scans all directories under ``wrfrun/res/``
2. **name_map Parsing**: It reads the ``name_map.json`` file in each directory
3. **Constant Generation**: It generates constant names by combining parent directory prefixes with the resource name
4. **URI Generation**: Each resource is mapped to a ``wrfrun://resource/`` URI
5. **Auto-registration**: The generated code automatically registers the resource URI with the framework

Generated Output
================
The script generates:

- Constants for each resource, pointing to their resource URI
- Automatic registration of the resource root URI
- Automatic setting of the main configuration template path
- Proper ``__all__`` export list

Generated __init__.py Example
=============================

The generated code looks like this:

.. code-block:: python
    :caption: wrfrun/res/__init__.py (generated)

    # Auto-generated file, do not edit manually!
    RUN_SH_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/run.template.sh"
    CONFIG_MAIN_TOML_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/config/config.template.toml"
    CONFIG_WRF_TOML_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/config/wrf.template.toml"
    # ... other constants

Using Resources
***************

To use a resource in your code, import the constant from ``wrfrun.res``:

.. code-block:: python

    from wrfrun.res import CONFIG_MAIN_TOML_TEMPLATE, SCHEDULER_PBS_TEMPLATE
    from wrfrun.core import WRFRUN

    # Get the actual file path by parsing the URI
    template_path = WRFRUN.config.parse_resource_uri(CONFIG_MAIN_TOML_TEMPLATE)
    
    # Use the path
    with open(template_path, 'r') as f:
        template_content = f.read()

All resources are referenced using URIs, which are automatically resolved to the correct physical path at runtime based on the installation location.

Adding New Resources
********************

Follow these steps to add a new resource:

1. **Add the file** to the appropriate directory under ``wrfrun/res/``
2. **Update name_map.json**: Add an entry for your new file in the corresponding directory's ``name_map.json``
3. **Rebuild the package**: Run command ``python wrfrun/res/generate_init.py -o wrfrun/res/__init__.py`` to regenerate ``__init__.py``
4. **Use the constant**: Import the generated constant in your code

Example: Adding a New Config Template
======================================

1. Add your template file: ``wrfrun/res/config/my_model.template.toml``
2. Update ``wrfrun/res/config/name_map.json``:

.. code-block:: json

    {
        // ... existing entries
        "my_model.template.toml": {
            "name": "MY_MODEL_TOML_TEMPLATE",
            "type": "file"
        }
    }

3. After running command ``python wrfrun/res/generate_init.py -o wrfrun/res/__init__.py``, you can use it:

.. code-block:: python

    from wrfrun.res import CONFIG_MY_MODEL_TOML_TEMPLATE

Example: Adding a New Resource Directory
========================================

1. Create the directory: ``wrfrun/res/my_new_dir/``
2. Add files to the directory
3. Create ``wrfrun/res/my_new_dir/name_map.json`` describing the contents
4. Add the directory to the root ``name_map.json``:

.. code-block:: json

    {
        // ... existing entries
        "my_new_dir": {
            "name": "MY_NEW_DIR",
            "type": "dir"
        }
    }

Best Practices
**************

1. **Never edit __init__.py directly**: Always modify ``name_map.json`` files and regenerate
2. **Use descriptive constant names**: Make constant names clear and self-documenting
3. **Group related resources**: Organize resources into appropriate subdirectories
4. **Test after adding**: Always verify that your new resource constant is generated correctly
5. **Use URIs always**: Never hardcode paths to resource files, always use the generated constants

Troubleshooting
***************

- **New resource not appearing**: Ensure you've added the entry to the correct ``name_map.json`` and regenerate ``__init__.py``
- **Invalid name_map.json**: Check for JSON syntax errors in your ``name_map.json`` files
- **Resource not found**: Verify the physical file exists and the path in name_map.json matches exactly
- **URI resolution issues**: Ensure you parse the URI using ``WRFRUN.config.parse_resource_uri()`` before using it as a file path

Next Steps
**********

- For core module development, see :doc:`develop_guide_core`
- For model integration, see :doc:`develop_guide_model`
- For the complete list of available resources, see the :doc:`/api/res` API documentation
