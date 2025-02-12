import cfgrib as cf
import numpy as np
from pandas import to_datetime
from seafog import goos_sst_find_data, goos_sst_parser
from xarray import DataArray

from .utils import create_sst_grib
from wrfrun.core import WRFRUNConfig
from wrfrun.utils import logger


def merge_era5_goos_sst_grib(surface_grib_path: str, save_path: str, resolution="low"):
    """
    This function can read ERA5 skt data from the surface GRIB file, interpolate it to the same resolution as GOOS sst data, merge them, and save it to a new GRIB file.

    Args:
        surface_grib_path: ERA5 surface GRIB file path.
        save_path: The save path of the new GRIB file.
        resolution: Resolution of GOOS sst, valid value: ``["low", "high"]``.

    """
    dataset_list = cf.open_datasets(surface_grib_path)

    dataset = None
    for _ds in dataset_list:
        if "skt" in _ds:
            dataset = _ds
            break

    if dataset is None:
        logger.error(f"'skt' data not found in {surface_grib_path}")
        raise ValueError

    skt = dataset["skt"]

    longitude_start, longitude_end = skt["longitude"][0].data, skt["longitude"][-1].data
    latitude_start, latitude_end = skt["latitude"][-1].data, skt["latitude"][0].data

    data_time = skt["time"].to_numpy()
    data_time = to_datetime(data_time).strftime("%Y-%m-%d %H:%M")

    sst_data_path = WRFRUNConfig.get_wrf_config()["near_goos_data_folder"]

    # read the first time data, so we can interpolate skt data to the same resolution as sst data.
    _data = goos_sst_find_data(data_time[0], sst_data_path, resolution=resolution, show_progress=False)
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
        _data = goos_sst_find_data(_data_time, sst_data_path, resolution=resolution, show_progress=False)
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
