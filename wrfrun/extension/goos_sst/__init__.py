"""
wrfrun.extension.goos_sst
#########################

This extension provides a method which can process NEAR-GOOS sea surface temperature (SST) data,
interpolate it to the ERA5 reanalysis data's grid and output a new GRIB file.
Please check :meth:`merge_era5_goos_sst_grib` to learn how to process the SST data.

This extension has three submodules:

================================================== =============================================
:doc:`goos_sst </api/extension.goos_sst.goos_sst>` Core functionality submodule.
:doc:`res </api/extension.goos_sst.res>`           Resource files provided by this extension.
:doc:`utils </api/extension.goos_sst.utils>`       Utility submodule used by the core submodule.
================================================== =============================================

.. toctree::
    :maxdepth: 1
    :hidden:

    goos_sst <extension.goos_sst.goos_sst>
    res <extension.goos_sst.res>
    utils <extension.goos_sst.utils>
"""

from .goos_sst import *
from .res import *
from .utils import *
