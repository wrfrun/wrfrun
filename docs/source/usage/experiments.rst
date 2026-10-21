Experiments
###########

Create an experiment skeleton with:

.. code-block:: console

   wrfrun experiment create v01

This command creates an ``experiment.toml`` override file and an experiment
namelist directory under ``configs/experiments/v01/``. It also creates empty
input, output, log, and runtime directories for the experiment.

The command does not copy or link common input data. Data snapshot and link
policies will be provided by a later workflow.
