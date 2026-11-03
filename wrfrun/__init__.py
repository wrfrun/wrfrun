"""
wrfrun
######

Run, configure, and manage numerical-model simulations.

Submodules
**********

=================================== ========================================================
:doc:`cli </api/cli>`               Command-line interface.
:doc:`core </api/core>`             Session runtime and executable services.
:doc:`data </api/data>`             ERA5 input-data download helpers.
:doc:`extension </api/extension>`   Optional model-data extensions.
:doc:`log </api/log>`               Application logging helpers.
:doc:`model </api/model>`           Model integrations and shared tools.
:doc:`plot </api/plot>`             General plotting utilities.
:doc:`res </api/res>`               Bundled package resources.
:doc:`run </api/run>`               Simulation context manager.
:doc:`scheduler </api/scheduler>`   Scheduler integration.
:doc:`utils </api/utils>`           General utility functions.
=================================== ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    cli <cli>
    core <core>
    data <data>
    extension <extension>
    log <log>
    model <model>
    plot <plot>
    res <res>
    run <run>
    scheduler <scheduler>
    utils <utils>
"""

from . import core, data, model, plot, res, run, scheduler, utils

__all__ = ["core", "data", "model", "plot", "res", "run", "scheduler", "utils"]
