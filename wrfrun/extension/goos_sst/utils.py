"""
wrfrun.extension.goos_sst.utils
###############################

Functions that are used by :doc:`/api/extension.goos_sst`.

.. autosummary::
    :toctree: generated/
    
    create_sst_grib
"""

from cfgrib.xarray_to_grib import to_grib
from numpy.dtypes import DateTime64DType
from pandas import to_datetime
from xarray import DataArray, Dataset

from wrfrun.utils import logger


def create_sst_grib(data: DataArray, save_path: str):
    """
    Write SST data to a GRIB file.
    
    This function creates GRIB file using ``cfgrib`` package.
    While GRIB write support is experimental in ``cfgrib``,
    this function may **FAIL TO CREATE GRIB FILE**.

    :param data: ``xarray.DataArray``, which at least has three dimensions: ``["time", "latitude", "longitude"]``.
    :type data: DataArray
    :param save_path: Output GRIB file path.
    :type save_path: str
    """
    # check the data's dimensions.
    for _dim in ["time", "longitude", "latitude"]:
        if _dim not in data.dims:
            logger.error(f"Essential dimension '{_dim}' not found in data")
            raise KeyError

    if not isinstance(data["time"].dtype, DateTime64DType):     # type: ignore
        data = data.assign_coords(time=to_datetime(data["time"].data))

    data = data.sortby(data["latitude"], ascending=False)

    longitude_start, longitude_stop = data["longitude"][0].data, data["longitude"][-1].data
    latitude_start, latitude_stop = data["latitude"][0].data, data["latitude"][-1].data
    delta_longitude = data["longitude"][1].data - data["longitude"][0].data
    delta_latitude = data["latitude"][0].data - data["latitude"][1].data
    longitude_length = data["longitude"].size
    latitude_length = data["latitude"].size
    points_number = data.size

    data = data.assign_attrs(**{
        "units": "K",
        "long_name": "Sea surface temperature",
        "standard_name": "Sea surface temperature",
        # The following keys and values will be used in GRIB.
        "GRIB_paramId": 34,
        "GRIB_shortName": "sst",
        "GRIB_units": "K",
        "GRIB_name": "Sea surface temperature",
        "GRIB_stepUnits": 1,
        "GRIB_stepType": "instant",
        "GRIB_gridType": "regular_ll",
        "GRIB_iDirectionIncrementInDegrees": delta_longitude,
        "GRIB_iScanNegatively": 0,
        "GRIB_jDirectionIncrementInDegrees": delta_latitude,
        "GRIB_jScanPositively": 0,
        "GRIB_latitudeOfFirstGridPointInDegrees": latitude_start,
        "GRIB_latitudeOfLastGridPointInDegrees": latitude_stop,
        "GRIB_longitudeOfFirstGridPointInDegrees": longitude_start,
        "GRIB_longitudeOfLastGridPointInDegrees": longitude_stop,
        "GRIB_Ny": latitude_length,
        "GRIB_Nx": longitude_length,
        "GRIB_typeOfLevel": "surface",
        # The following keys and values can't be found at ECMWF websites.
        "GRIB_cfName": "unknown",
        "GRIB_cfVarName": "sst",
        "GRIB_dataType": "an",  # Analysis data, defined at https://codes.ecmwf.int/grib/format/mars/type/
        "GRIB_gridDefinitionDescription": "Latitude/Longitude Grid",
        # "GRIB_missingValue": -9999,
        "GRIB_numberOfPoints": points_number,
        "GRIB_totalNumber": 0,
        "GRIB_uvRelativeToGird": 0
    })

    to_grib(
        Dataset({
            "sst": data
        }, attrs={
            "GRIB_centre": "ecmf",
            "GRIB_edition": 1,
        }), save_path
    )


__all__ = ["create_sst_grib"]
