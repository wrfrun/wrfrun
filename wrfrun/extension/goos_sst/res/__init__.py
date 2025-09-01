"""
wrfrun.extension.goos_sst.res
#############################

Resource files provided by :doc:`/api/extension.goos_sst`.

VTABLE_ERA_GOOS_SST
*******************

.. py:data:: VTABLE_ERA_GOOS_SST
    :type: str
    :value: Absolute file path.

    Vtable file used to input the GRIB data created by :doc:`/api/extension.goos_sst` to WRF.

"""

from os.path import abspath, dirname


_PATH = abspath(dirname(__file__))

VTABLE_ERA_GOOS_SST = f"{_PATH}/Vtable.ERA_GOOS_SST"


__all__ = ["VTABLE_ERA_GOOS_SST"]
