"""
wrfrun.extension.goos_sst.core
##############################

Implementation of ``extension.goos_sst``'s core functionality.


.. autosummary::
    :toctree: generated/
    
    merge_era5_goos_sst_grib
"""

from os.path import dirname

import cfgrib as cf
import numpy as np
from pandas import to_datetime
from xarray import DataArray

from .utils import create_sst_grib
from wrfrun.utils import logger


def merge_era5_goos_sst_grib(surface_grib_path: str, save_path: str, sst_data_save_path: str | None = None, resolution="low"):
    """
    This function reads ERA5 skin temperature (SKT) data from the GRIB file,
    interpolates it to the same grib of NEAR-GOOS sea surface temperature (SST) data,
    merges them and creates a new GRIB file with the new data.

    :param surface_grib_path: GRIB file which contains SKT data.
    :type surface_grib_path: str
    :param save_path: Save path of the new GRIB file.
    :type save_path: str
    :param sst_data_save_path: Save path of downloaded NEAR-GOOS SST data.
                               If None, save data to the parent directory of ``save_path``.
    :type sst_data_save_path: str | None
    :param resolution: Resolution of downloaded NEAR-GOO SST data.
                       Please check ``seafog.goos_sst_find_data`` for more information.
    :type resolution: str
    """
    # lazy import seafog to fix libcurl error in readthedocs
    # T^T
    from seafog import goos_sst_find_data, goos_sst_parser

    dataset_list = cf.open_datasets(surface_grib_path)

    dataset = None
    for _ds in dataset_list:
        if "skt" in _ds:
            dataset = _ds
            break

    if dataset is None:
        logger.error(f"'skt' data not found in {surface_grib_path}")
        raise ValueError

    skt: DataArray = dataset["skt"]     # type: ignore

    longitude_start, longitude_end = skt["longitude"][0].data, skt["longitude"][-1].data    # type: ignore
    latitude_start, latitude_end = skt["latitude"][-1].data, skt["latitude"][0].data    # type: ignore

    data_time = skt["time"].to_numpy()  # type: ignore
    data_time = to_datetime(data_time).strftime("%Y-%m-%d %H:%M")

    if sst_data_save_path is None:
        sst_data_save_path = dirname(save_path)

    # read the first time data, so we can interpolate skt data to the same resolution as sst data.
    _data = goos_sst_find_data(data_time[0], sst_data_save_path, resolution=resolution, show_progress=False)
    _data = goos_sst_parser(_data, resolution=resolution)
    _data = _data.loc[latitude_start:latitude_end, longitude_start:longitude_end]

    skt = skt.interp({"longitude": _data["longitude"], "latitude": _data["latitude"]})
    sst = np.zeros_like(skt)
    temp_data = np.zeros_like(skt[0])

    temp_data[:] = skt.to_numpy()[0]
    index = ~np.isnan(_data.to_numpy())
    temp_data[index] = _data.to_numpy()[index]
    sst[0] = temp_data

    # loop other time.
    for time_index, _data_time in enumerate(data_time[1:], start=1):
        _data = goos_sst_find_data(_data_time, sst_data_save_path, resolution=resolution, show_progress=False)
        _data = goos_sst_parser(_data, resolution=resolution)
        _data = _data.loc[latitude_start:latitude_end, longitude_start:longitude_end]

        temp_data[:] = skt.to_numpy()[time_index]
        index = ~np.isnan(_data.to_numpy())
        temp_data[index] = _data.to_numpy()[index]
        sst[time_index] = temp_data

    sst = DataArray(
        name="sst",
        data=sst,
        dims=["time", "latitude", "longitude"],
        coords={
            "time": skt["time"],
            "latitude": skt["latitude"],
            "longitude": skt["longitude"]
        }, attrs={
            "units": "K",
            "long_name": "Sea surface temperature"
        }
    )

    create_sst_grib(sst, save_path=save_path)


__all__ = ["merge_era5_goos_sst_grib"]
