Context
#######

:class:`WRFRun <wrfrun.run.WRFRun>` is the core context manager of the ``wrfrun`` framework, designed to encapsulate all the setup, execution, 
and cleanup logic required for running numerical model simulations. 
It handles configuration loading, workspace preparation, job scheduling, progress monitoring, and resource cleanup automatically.

How It Works
************

The :class:`WRFRun <wrfrun.run.WRFRun>` context manager operates in two phases:

+ **Entry Phase (``__enter__`` method)**:
   - Loads and validates the configuration file
   - Prepares and cleans the workspace directory
   - Validates domain configurations and optionally asks for user confirmation
   - Submits the job to a cluster scheduler if enabled
   - Starts the progress monitoring socket server if enabled
   - Downloads ERA5 input data if requested
   - Configures logging and saves a copy of the configuration to the output directory

+ **Exit Phase (``__exit__`` method)**:
   - Stops the progress monitoring server if it was running
   - Exports simulation replay files if recording was enabled
   - Cleans up temporary resources and logs
   - Updates the context state to mark the simulation as completed

Basic Usage
***********

The simplest way to use :class:`WRFRun <wrfrun.run.WRFRun>` is to wrap your simulation code in a ``with`` block:

.. code-block:: python
    :caption: Basic usage example

    from wrfrun.run import WRFRun
    from wrfrun.model.wrf import geogrid, ungrib, metgrid, real, wrf

    with WRFRun("config.toml") as wrf_run:
        # All your simulation code goes here
        geogrid()
        ungrib()
        metgrid()
        real()
        wrf()

Constructor Parameters
**********************

The :class:`WRFRun <wrfrun.run.WRFRun>` constructor accepts several parameters to customize its behavior:

.. list-table::
    :widths: 25 60 15
    :header-rows: 1

    * - Parameter
      - Description
      - Default
    * - ``config_file``
      - Path to the TOML configuration file for your simulation
      - *Required*
    * - ``init_workspace``
      - If ``True``, cleans and reinitializes the workspace directory before running
      - ``True``
    * - ``start_server``
      - If ``True``, starts a lightweight socket server to report simulation progress in real-time
      - ``False``
    * - ``submit_job``
      - If ``True``, submits the simulation to the configured job scheduler (PBS/Slurm/LSF) instead of running locally
      - ``False``
    * - ``prepare_wps_data``
      - If ``True``, automatically downloads ERA5 input data for WPS before starting the simulation
      - ``False``
    * - ``wps_data_area``
      - Tuple defining the geographic area for data download when ``prepare_wps_data=True``: ``(min_lon, max_lon, min_lat, max_lat)``
      - ``None``
    * - ``skip_domain_confirm``
      - If ``True``, skips the interactive domain confirmation prompt
      - ``False``

Key Features
************

Workspace Preparation
=====================

When ``init_workspace=True``, :class:`WRFRun <wrfrun.run.WRFRun>` automatically:

- Creates all required directory structure (workspace, outputs, logs)
- Cleans up any leftover files from previous runs
- Validates that all required paths and resources are available

Job Scheduling
==============

When running on a cluster, set ``submit_job=True`` to automatically:

- Generate the appropriate job submission script based on your scheduler configuration
- Validate your domain configuration before submission
- Submit the job to the scheduler
- Exit immediately after submission without running the simulation locally

Progress Monitoring
===================

Enable real-time progress monitoring by setting ``start_server=True``:

- Starts a socket server that reports simulation progress, remaining time, and current step
- Accessible via the configured host and port in your configuration file
- Can be integrated with monitoring tools or dashboards

Simulation Recording and Replay
===============================

``WRFRun`` provides built-in support for recording and replaying simulations to ensure reproducibility, for example:

.. code-block:: python
    :caption: Recording a simulation

    with WRFRun("config.toml") as wrf_run:
        # Start recording the simulation
        wrf_run.record_simulation(output_path="./outputs/my_simulation.replay")
        
        # Run your simulation steps
        geogrid()
        ungrib()
        metgrid()
        real()
        wrf()

.. code-block:: python
    :caption: Replaying a recorded simulation

    with WRFRun("config.toml") as wrf_run:
        # Replay the entire simulation automatically
        wrf_run.replay_simulation("./outputs/my_simulation.replay")

.. code-block:: python
    :caption: Iterating through recorded steps

    with WRFRun("config.toml") as wrf_run:
        # Iterate through each recorded executable step
        for name, executable in wrf_run.replay_executables("./outputs/my_simulation.replay"):
            print(f"Running step: {name}")
            executable()

Automatic Data Download
=======================

To automatically download ERA5 input data for your WPS simulation:

.. code-block:: python
    :caption: Downloading ERA5 data automatically

    # Download data for area: 90°E - 180°E, 10°N - 70°N
    with WRFRun("config.toml", 
                prepare_wps_data=True,
                wps_data_area=(90, 180, 10, 70)) as wrf_run:
        # Data will be downloaded automatically before entering the context
        geogrid()
        ungrib()
        metgrid()
        # ... rest of your simulation

.. note::
    Automatic ERA5 download requires you to have `cdsapi` configured with your API credentials. See the `CDS API documentation <https://cds.climate.copernicus.eu/how-to-api>`_ for setup instructions.

Best Practices
**************

+ **Always use the context manager**: Never instantiate :class:`WRFRun <wrfrun.run.WRFRun>` directly without the ``with`` block, as this will leave resources unmanaged and may cause unexpected behavior.
+ **Use relative paths**: Configuration file paths are resolved relative to the directory of your entry script, so using relative paths makes your code more portable.
+ **Enable recording for important simulations**: Always record simulations that you want to reproduce later, as the replay file contains all the information needed to rerun exactly the same simulation on any machine.
+ **Skip domain confirmation in scripts**: When running automated or non-interactive scripts, set ``skip_domain_confirm=True`` to avoid waiting for user input.
+ **Separate configuration from code**: Keep all simulation settings in the TOML configuration file rather than hardcoding them in your Python scripts for better maintainability.
