Installation
############

This guide will help you install ``wrfrun`` on your system.

Prerequisites
*************

Before installing ``wrfrun``, make sure you have the following:

- Python 3.10 or higher
- Python package manager (pip or uv)
- For WRF model usage: A working WRF/WPS installation (You can use `WRF-Install-Script <https://github.com/bakamotokatas/WRF-Install-Script>`_ to install WRF)
- For PALM model usage: A working PALM installation

System Requirements
===================

- Operating System: Linux
- Memory: Minimum 4GB RAM, 8GB+ recommended for model runs
- Disk Space: Sufficient space for model data and outputs

Installing wrfrun
******************

Method 1: Using pip or uv (Recommended)
=======================================

The easiest way to install ``wrfrun`` is using pip or uv:

.. code-block:: bash

    pip install wrfrun
    # or
    uv add wrfrun

Method 2: From Source
======================

If you want to install the latest development version or contribute to the project, you can install from source:

.. code-block:: bash

    # pip install git+https://github.com/Syize/wrfrun.git@{branch}, for example
    pip install git+https://github.com/Syize/wrfrun.git@master
    # or
    uv add "wrfrun @ git+https://github.com/Syize/wrfrun.git"

Optional Dependencies
*********************

Some features of ``wrfrun`` require additional dependencies:

- **ERA5 data download**: Requires ``cdsapi`` (installed by default)
- **Plotting features**: Requires ``matplotlib`` and ``Cartopy`` (installed by default)
- **WRF data processing**: Requires ``wrf-python`` (optional, install separately if needed)

To install optional dependencies:

.. code-block:: bash

    pip install wrf-python

Verifying Installation
**********************

To verify that ``wrfrun`` is installed correctly, run:

.. code-block:: bash

    python -c "import wrfrun; print(wrfrun.__name__)"

If this prints ``wrfrun`` without errors, the installation was successful.

Next Steps
**********

Now that you have ``wrfrun`` installed, you can:

1. Check out the :doc:`quick_start` guide to get started with a simple example
2. Learn about the :doc:`../documentation/config_file` format
3. Explore the :doc:`../api/index` for detailed API documentation

Troubleshooting
***************

If you encounter installation issues, make sure you're using Python 3.10 or newer:

.. code-block:: bash

    python --version

