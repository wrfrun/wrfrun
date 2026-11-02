wrfrun documentation
####################

``wrfrun`` is a Python toolkit for organizing numerical-model simulations as
repeatable, inspectable workflows. It keeps the model-specific work—writing
namelists, staging inputs, running external programs, and collecting
outputs—close to the model interface, while providing one project layout for
configuration, experiments, logs, archived results, and isolated runtime
workspaces.

It is useful when a simulation involves more than one executable or must be
repeated with small configuration changes. A supported model is invoked from a
short Python script inside :class:`WRFRunContext <wrfrun.run.WRFRunContext>`; ``wrfrun`` then
prepares that run's workspace and records its files and outputs in the project.

What wrfrun provides
*********************

- **Model interfaces** for external numerical-model executables. An executable
  owns its namelist preparation, input staging, command execution, and output
  collection.
- **Project and experiment management**. A project can contain several named
  experiments, each with its own configuration overrides, namelist updates,
  input-data directory, outputs, and logs.
- **Isolated runs and result archives**. Each run receives an independent
  workspace and immutable output archive. ``results/<executable>`` points to
  the latest published output for a later stage of the same experiment.
- **Reproducibility tools**. The runtime records executable configuration and
  file handoffs for replay; a :class:`ResultSource <wrfrun.core.type.ResultSource>`
  can explicitly select an upstream result from another experiment or run.
- **Cluster support**. Scheduler scripts can be rendered from project-provided
  templates and submitted through supported scheduler backends.

Typical workflow
****************

1. Create a project and enable the numerical-model plugins you need.

   .. code-block:: console

      $ wrfrun init --path my-project --models arps

2. Prepare the model namelist templates and user updates under ``configs/``.

   .. code-block:: console

      $ cd my-project
      $ $EDITOR config.toml
      $ $EDITOR configs/namelists/templates/arps/arps/arps.nml  # All namelist settings
      $ $EDITOR configs/namelists/templates/arps/arps/arps.nml  # Only the value you want to change

3. Place the input files needed for the first simulation under the default
   ``common`` input directory.

   .. code-block:: console

      $ mkdir -p data/inputs/common/<executable>
      $ cp <input-files> data/inputs/common/<executable>/

4. Enter a :class:`WRFRunContext <wrfrun.run.WRFRunContext>` context and call model wrappers
   in the required order. Each executable stages its declared inputs, runs in
   the active isolated workspace, and archives its outputs.

   .. code-block:: python

      from wrfrun.run import WRFRunContext
      from wrfrun.model.arps import arps

      with WRFRunContext("config.toml"):
          arps()

5. Inspect logs and archived outputs, or use a published result as the input to
   a later simulation stage.

   .. code-block:: console

      $ wrfrun jobs --config config.toml
      $ wrfrun jobs --config config.toml --follow <run-id>

   .. code-block:: python

      from wrfrun.core import ResultSource

      source = ResultSource(executable="arps", run_id="<run-id>")

Start here
**********

- :doc:`Usage guide </usage/index>` explains installation, project creation,
  the first simulation, experiments, jobs, profiles, and custom executables.
- :doc:`Quick start </usage/quick_start>` is the practical entry point for a
  first WRF workflow.
- :doc:`Experiments </usage/experiments>` describes how related simulations are
  organized within one project.
- :doc:`Jobs </usage/jobs>` documents status inspection and following an active
  executable log.

Understand a project and run
****************************

- :doc:`Configuration </documentation/config_file>` describes the top-level,
  model, and experiment TOML files.
- :doc:`Runtime context </documentation/context>` explains what happens when a
  ``WRFRun`` context starts, how outputs are archived, and how replay works.
- :doc:`Concepts and configuration </documentation/index>` collects the
  remaining architecture and configuration material.

Reference and development
*************************

- :doc:`API reference </api/index>` documents the public Python and command
  line interfaces.
- :doc:`Development guide </development/index>` is for model-plugin and core
  contributors.

.. toctree::
   :maxdepth: 2
   :hidden:

   usage/index
   documentation/index
   api/index
   development/index
