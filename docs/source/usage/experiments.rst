Experiments
###########

Create an experiment skeleton with:

.. code-block:: console

   wrfrun experiment create v01
   wrfrun experiment create v02 --copy

This command creates an ``experiment.toml`` override file and an experiment
namelist directory under ``configs/experiments/v01/``. It also creates empty
input, output, log, and runtime directories for the experiment. By default,
each common input file is represented by a relative symbolic link in the new
experiment input directory. Use ``--copy`` to create independent input files.

The experiment directory has its own input tree, so a file can later be
replaced or added without changing the common inputs or another experiment.

Model plugins create their namelist directories when the model is added. A
namelist is read from the project template, then updated by the matching global
user file and experiment file. For example, WRF reads:

.. code-block:: text

   configs/namelists/templates/wrf/wrf/namelist.input
   configs/namelists/user/wrf/wrf/namelist.input
   configs/experiments/v01/namelists/wrf/wrf/namelist.input

The first file is required. The latter two are optional and override values in
the order shown.

``experiment.toml`` overrides the matching values in ``config.toml`` and in
the enabled model configuration. TOML tables are merged recursively, so it
only needs to contain the values that differ. For example:

.. code-block:: toml

   [simulation.time]
   end_time = 2025-12-02T00:00:00+00:00

   [model.arps.global]
   grid_dx = 500.0

Run an experiment from Python with:

.. code-block:: python

   from wrfrun.run import WRFRunContext

   with WRFRunContext("config.toml", experiment="v01"):
       ...

Every context creates a unique run ID. Its workspace, replay files, temporary
files, outputs, and logs are isolated from other runs of the same experiment.
