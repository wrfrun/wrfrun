"""
wrfrun.workspace
################

Prepare ``workspace`` for ``wrfrun`` and numerical models.

Submodules
**********

=================================    ===========================================================
:doc:`core </api/workspace.core>`    Core functions of this submodule.
:doc:`palm </api/workspace.palm>`    Functions to prepare workspace for PALM model.
:doc:`wrf </api/workspace.wrf>`      Functions to prepare workspace for WPS/WRF model.
=================================    ===========================================================

Workspace
*********

``workspace`` is a collection of several directories where ``wrfrun``, extensions and numerical model works.
These directories and their purpose are listed below. ``$ROOT`` is the root work path set in config file,
or ``$HOME/.config/wrfrun``.

===================================         ===========================================================
Director Path                               Purpose
===================================         ===========================================================
``$ROOT``                                   Main work directory.
``$ROOT/tmp``                               Store temporary files.
``$ROOT/replay``                            Work directory for :doc:`replay </api/core.replay>`.
``$ROOT/workspace``                         Work directory for numerical models.
===================================         ===========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    core <workspace.core>
    palm <workspace.palm>
    wrf <workspace.wrf>
"""

from .core import *
