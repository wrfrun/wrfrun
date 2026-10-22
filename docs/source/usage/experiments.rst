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
