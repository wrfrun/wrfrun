"""
wrfrun.extension.goos_sst
#########################

This extension can help you create a GRIB file from ERA5 skin temperature (SKT) data and NEAR-GOOS sea surface temperature (SST) data.

============================================= =============================================
:doc:`core </api/extension.goos_sst.core>`    Core functionality submodule.
:doc:`res </api/extension.goos_sst.res>`      Resource files provided by this extension.
:doc:`utils </api/extension.goos_sst.utils>`  Utility submodule used by the core submodule.
============================================= =============================================

Important Note
**************

This extension relies on ``cfgrib`` package to create GRIB file.
While GRIB write support is experimental in ``cfgrib``,
this extension may **FAIL TO CREATE GRIB FILE**.

How This Extension Works
************************

This extension provides a method which merges ERA5 reanalysis skin temperature (SKT) data and NEAR-GOOS SST data,
and write new data to a GRIB file.

How To Use This Extension
*************************

Prerequisite
============

You need to have the following packages installed, because they are not included in ``wrfrun``'s dependency:

* cfgrib: Provide the method to create GRIB file.
* seafog: Provide the method to download and read NEAR-GOOS SST data.

And you also have downloaded an ERA5 reanalysis data (GRIB format) which contains SKT data.

How To Use
==========

The code snap below shows you how to use this extension.

.. code-block:: Python
    :caption: main.py

    from wrfrun.extension.goos_sst import merge_era5_goos_sst_grib


    if __name__ == '__main__':
        era5_data_path = "data/ear5-reanalysis-data.grib"
        merge_era5_goos_sst_grib(era5_data_path, "data/near-goos-data.grib")
        
Please check :func:`core.merge_era5_goos_sst_grib` for more information.

.. toctree::
    :maxdepth: 1
    :hidden:

    core <extension.goos_sst.core>
    res <extension.goos_sst.res>
    utils <extension.goos_sst.utils>
"""

from .core import *
from .res import *
from .utils import *
