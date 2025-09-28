"""
wrfrun.workspace
################

Prepare ``workspace`` for ``wrfrun`` and numerical models.

Submodules
**********

=================================    ===========================================================
:doc:`core </api/workspace.core>`    Core functions of this submodule.
:doc:`wrf </api/workspace.wrf>`      Functions to prepare workspace for WPS/WRF model.
=================================    ===========================================================

Workspace
*********

``workspace`` is a collection of several directories where ``wrfrun``, extensions and numerical model works.
These directories and their purpose are listed below.

===================================         ===========================================================
Director Path                               Purpose
===================================         ===========================================================
``/tmp/wrfrun``                             Store temporary files.
``$HOME/.config/wrfrun``                    Main work directory.
``$HOME/.config/wrfrun/replay``             Work directory for :doc:`replay <wrfrun.core.replay>`.
``$HOME/.config/wrfrun/model``              Work directory for numerical models.
===================================         ===========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    core <workspace.core>
    wrf <workspace.wrf>
"""

from .core import *
