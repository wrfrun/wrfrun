.. wrfrun documentation master file, created by
   sphinx-quickstart on Sun Feb 16 12:49:45 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

wrfrun documentation
####################

.. note::
   I'm still working on to complete ``wrfrun``'s documentation, you'll find some empty pages, which is normal :)

   I hope you like my work.

🌀 What is wrfrun?
******************

``wrfrun`` is a modern, unified framework for running and managing numerical models. Designed for researchers who want to focus on science — not on the details of model execution.

It automates the tedious parts of model execution — preparing input data, handling ``namelist`` configurations, organizing logs, and submitting jobs — so that you can spend your time on research, not on managing model runs.

``wrfrun`` is not just limited to WRF; it provides a general-purpose, reproducible, and extensible framework that can be adapted to various numerical models through its unified interface architecture.

✨ Core Features
****************

🧩 Unified Interface Architecture
=================================

``wrfrun`` enforces a unified interface specification for all numerical models. Specifically, each model interface must inherit from a provided base class, ensuring a consistent structure and behavior across different models.

This design makes model execution intuitive — any supported model can be launched simply by calling a Python function or class method, while ``wrfrun`` automatically handles all background tasks such as data preparation and configuration file management.

.. code-block:: python
   
   from wrfrun.run import WRFRun
   from wrfrun.model.wrf import geogrid, metgrid, real, ungrib, wrf

   # wrfrun will prepare input data, generate namelist file,
   # save outputs and logs automatically.
   with WRFRun("./config.toml", init_workspace=True) as wrf_run:
       geogrid()
       ungrib()
       metgrid()
       real()
       wrf()

🪶 Record & Replay
===================

Every simulation can be fully recorded and later reproduced from a single ``.replay`` file — ensuring total reproducibility.

.. code-block:: python

   from wrfrun.run import WRFRun
   from wrfrun.model.wrf import geogrid, ungrib, metgrid, real, wrf


   # 1. Record simulation with method `record_simulation`.
   with WRFRun("./config.toml", init_workspace=True) as wrf_run:
       wrf_run.record_simulation(output_path="./outputs/example.replay")

       geogrid()
       ungrib()
       metgrid()
       real()
       wrf()

   # 2. Replay the simulation in a different directory or on a different machine.
   with WRFRun("./config.toml", init_workspace=True) as wrf_run:
       wrf_run.replay_simulation("./example.replay")

⚙️ Simplified Configuration
============================

Manage all simulation settings in TOML files: A main config file, and model config files.

.. code-block:: toml

   # main config file: config.toml
   work_dir = "./.wrfrun"

   input_data_path = ""
   output_path = "./outputs"
   log_path = "./logs"

   server_host = "localhost"
   server_port = 54321

   core_num = 36

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

``wrfrun`` remains compatible with original ``namelist`` inputs, just set namelist file path in the model config.

💻 Job Scheduling Integration
==============================

Automatically submit jobs to supported schedulers:

- PBS
- Slurm
- LSF

``wrfrun`` takes care of resource requests and queue management automatically.

.. code-block:: python

   from wrfrun.run import WRFRun
   from wrfrun.model.wrf import geogrid, metgrid, real, ungrib, wrf

   # just set submit_job=True
   with WRFRun("./config.toml", init_workspace=True, submit_job=True) as wrf_run:
       geogrid()
       ungrib()
       metgrid()
       real()
       wrf()

📡 Real-time Monitoring
========================

``wrfrun`` can parse model log files and start a lightweight socket server to report simulation progress.

.. code-block:: python

   from wrfrun.run import WRFRun
   from wrfrun.model.wrf import geogrid, metgrid, real, ungrib, wrf

   # just set start_server=True
   with WRFRun("./config.toml", init_workspace=True, start_server=True) as wrf_run:
       geogrid()
       ungrib()
       metgrid()
       real()
       wrf()

🌍 Current Capabilities
************************

- Automated ERA5 data download (requires ``cdsapi`` authentication)
- Real-time progress reporting via socket interface
- Numerical model support:
   * Partial WRF support:
      + Full support for WPS
      + Wrapped execution for ``real`` and ``wrf``
   * PALM model support (in progress)
- Job submission on PBS, Slurm, and LSF
- ``record`` / ``replay`` reproducibility for all compliant interfaces

Get started
***********

These sections will teach you how to install ``wrfrun``, and help you explore ``wrfrun`` using the same cases from `WRF–ARW Online Tutorial <https://www2.mmm.ucar.edu/wrf/OnLineTutorial/>`_.

.. toctree::
   :maxdepth: 3
   :caption: Get started:

   usage/index

User guide
**********

These sections will explain important concepts of ``wrfrun`` and help you understand how ``wrfrun`` works.

.. toctree::
   :maxdepth: 3
   :caption: User guide:

   documentation/index

API reference
*************

:doc:`/api/index` contains a detailed description of the ``wrfrun`` API. It describes how the methods work and which parameters can be used.

.. toctree::
   :hidden:
   :maxdepth: 2

   api/index

.. toctree::
   :hidden:
   :maxdepth: 2

   development/index
