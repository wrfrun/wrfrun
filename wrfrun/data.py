"""
wrfrun.data
###########

.. autosummary::
    :toctree: generated/

    ERA5CONFIG
    _check_variables_and_datasets
    _check_pressure_level
    find_era5_data
    prepare_wps_input_data
    download_data
"""

from datetime import datetime
from os import makedirs
from os.path import dirname, exists
from typing import List, Literal, Tuple, Union

from pandas import date_range

from .core import WRFRUN
from .log import logger

# from seafog import goos_sst_find_data

# lazy initialize
CDS_CLIENT = None


class ERA5CONFIG:
    """
    A class to store parameters we will use to download ERA5 data from cdsapi.

    .. py:attribute:: DATASET_ERA5_SINGLE_LEVEL
        :type: str
        :value: "reanalysis-era5-single-levels"

        ERA5 dataset type.

    .. py:attribute:: DATASET_ERA5_PRESSURE_LEVEL
        :type: str
        :value: "reanalysis-era5-pressure-levels"

        ERA5 dataset type.

    .. py:attribute:: TYPE_REANALYSIS
        :type: str
        :value: "reanalysis"

        ERA5 product type.

    .. py:attribute:: FORMAT_NETCDF
        :type: str
        :value: "netcdf"

        ERA5 data format type.

    .. py:attribute:: FORMAT_GRIB
        :type: str
        :value: "grib"

        ERA5 data format type.

    .. py:attribute:: DOWNLOAD_ZIP
        :type: str
        :value: "zip"

        ERA5 download type.

    .. py:attribute:: DOWNLOAD_UNZIP
        :type: str
        :value: "unarchived"

        ERA5 download type.

    .. py:attribute:: PRESSURE_LEVEL
        :type: list

        ERA5 available pressure levels.

    .. py:attribute:: VARIABLE_*
        :type: str

        ERA5 variable names. Please check the code to see available values (too many to list here).

    .. py:attribute:: NAME_MAP
        :type: dict

        Dictionary maps variable to its name in data.

    .. py:attribute:: TYPE_MAP
        :type: dict

        Dictionary to distinguish between two types of data.
    """

    # dataset name
    DATASET_ERA5_SINGLE_LEVEL = "reanalysis-era5-single-levels"
    DATASET_ERA5_PRESSURE_LEVEL = "reanalysis-era5-pressure-levels"

    # type name
    TYPE_REANALYSIS = "reanalysis"

    # format name
    FORMAT_NETCDF = "netcdf"
    FORMAT_GRIB = "grib"

    # download format
    DOWNLOAD_ZIP = "zip"
    DOWNLOAD_UNZIP = "unarchived"

    # all level
    PRESSURE_LEVEL = [
        "1",
        "2",
        "3",
        "5",
        "7",
        "10",
        "20",
        "30",
        "50",
        "70",
        "100",
        "125",
        "150",
        "175",
        "200",
        "225",
        "250",
        "300",
        "350",
        "400",
        "450",
        "500",
        "550",
        "600",
        "650",
        "700",
        "750",
        "775",
        "800",
        "825",
        "850",
        "875",
        "900",
        "925",
        "950",
        "975",
        "1000",
    ]

    # variable name
    VARIABLE_2M_TEMPERATURE = "2m_temperature"
    VARIABLE_2M_DEWPOINT_TEMP = "2m_dewpoint_temperature"
    VARIABLE_LANDSEA_MASK = "land_sea_mask"
    VARIABLE_MEAN_SEA_LEVEL_PRESSURE = "mean_sea_level_pressure"
    VARIABLE_SKIN_TEMPERATURE = "skin_temperature"
    VARIABLE_SNOW_DENSITY = "snow_density"
    VARIABLE_SNOW_DEPTH = "snow_depth"
    VARIABLE_SOIL_TEMP_LEVEL_1 = "soil_temperature_level_1"
    VARIABLE_SOIL_TEMP_LEVEL_2 = "soil_temperature_level_2"
    VARIABLE_SOIL_TEMP_LEVEL_3 = "soil_temperature_level_3"
    VARIABLE_SOIL_TEMP_LEVEL_4 = "soil_temperature_level_4"
    VARIABLE_SURFACE_PRESSURE = "surface_pressure"
    VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_1 = "volumetric_soil_water_layer_1"
    VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_2 = "volumetric_soil_water_layer_2"
    VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_3 = "volumetric_soil_water_layer_3"
    VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_4 = "volumetric_soil_water_layer_4"
    VARIABLE_10M_U_WIND = "10m_u_component_of_wind"
    VARIABLE_10M_V_WIND = "10m_v_component_of_wind"
    VARIABLE_U_WIND = "u_component_of_wind"
    VARIABLE_V_WIND = "v_component_of_wind"
    VARIABLE_SPECIFIC_HUMIDITY = "specific_humidity"
    VARIABLE_RELATIVE_HUMIDITY = "relative_humidity"
    VARIABLE_GEOPOTENTIAL = "geopotential"
    VARIABLE_TEMPERATURE = "temperature"

    # name in downloaded data
    NAME_MAP = {
        "2m_temperature": "t2m",
        "10m_u_component_of_wind": "u10",
        "u_component_of_wind": "u",
        "v_component_of_wind": "v",
        "10m_v_component_of_wind": "v10",
        "specific_humidity": "q",
        "geopotential": "z",
        "relative_humidity": "r",
        "temperature": "t",
        "2m_dewpoint_temperature": "d2m",
        "land_sea_mask": "lsm",
        "mean_sea_level_pressure": "msl",
        "skin_temperature": "skt",
        "snow_density": "rsn",
        "snow_depth": "sd",
        "soil_temperature_level_1": "stl1",
        "soil_temperature_level_2": "stl2",
        "soil_temperature_level_3": "stl3",
        "soil_temperature_level_4": "stl4",
        "surface_pressure": "sp",
        "volumetric_soil_water_layer_1": "swvl1",
        "volumetric_soil_water_layer_2": "swvl2",
        "volumetric_soil_water_layer_3": "swvl3",
        "volumetric_soil_water_layer_4": "swvl4",
    }

    # use a dict to distinguish between two types of data
    TYPE_MAP = {
        "reanalysis-era5-single-levels": (
            "2m_temperature",
            "2m_dewpoint_temperature",
            "land_sea_mask",
            "skin_temperature",
            "snow_density",
            "snow_depth",
            "mean_sea_level_pressure",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "soil_temperature_level_1",
            "soil_temperature_level_2",
            "soil_temperature_level_3",
            "soil_temperature_level_4",
            "surface_pressure",
            "volumetric_soil_water_layer_1",
            "volumetric_soil_water_layer_2",
            "volumetric_soil_water_layer_3",
            "volumetric_soil_water_layer_4",
        ),
        "reanalysis-era5-pressure-levels": (
            "specific_humidity",
            "u_component_of_wind",
            "v_component_of_wind",
            "geopotential",
            "relative_humidity",
            "temperature",
        ),
    }


def _check_variables_and_datasets(variables: Union[str, Tuple[str, ...]], dataset: str) -> bool:
    """
    Check if variables and datasets correspond.

    :param variables: Variables type.
    :type variables: Union[str, Tuple[str, ...]]
    :param dataset: Dataset type.
    :type dataset: str
    :return: If check passed, return ``True``, else ``False``.
    :rtype: bool
    """
    if isinstance(variables, str):
        if variables in ERA5CONFIG.TYPE_MAP[dataset]:
            return True
        else:
            return False
    else:
        for variable in variables:
            if variable not in ERA5CONFIG.TYPE_MAP[dataset]:
                return False

        return True


def _check_pressure_level(pressure_level: Union[str, List[str]]) -> bool:
    """
    Check pressure level.

    :param pressure_level: A integer value or a list contains pressure values.
    :type pressure_level: Union[str, List[str]]
    :return: If check passed, return ``True``, else ``False``.
    :rtype: bool
    """
    valid_pressure_level = [
        "1",
        "2",
        "3",
        "5",
        "7",
        "10",
        "20",
        "30",
        "50",
        "70",
        "100",
        "125",
        "150",
        "175",
        "200",
        "225",
        "250",
        "300",
        "350",
        "400",
        "450",
        "500",
        "550",
        "600",
        "650",
        "700",
        "750",
        "775",
        "800",
        "825",
        "850",
        "875",
        "900",
        "925",
        "950",
        "975",
        "1000",
    ]

    for level in pressure_level:
        if level not in valid_pressure_level:
            return False

    return True


def find_era5_data(
    date: Union[List[str], List[datetime]],
    area: Tuple[int, int, int, int],
    variables: Union[Tuple[str, ...], str],
    save_path: str,
    product_type=ERA5CONFIG.TYPE_REANALYSIS,
    data_format=ERA5CONFIG.FORMAT_NETCDF,
    dataset=ERA5CONFIG.DATASET_ERA5_SINGLE_LEVEL,
    download_format=ERA5CONFIG.DOWNLOAD_UNZIP,
    pressure_level: Union[int, List[int], str, List[str], None] = None,
    overwrite=False,
) -> str:
    """
    Download data from ERA5.

    :param date: List of date string or datetime object, UTC time.
    :type date: Union[List[str], List[datetime]]
    :param area: Range of longitude and latitude, ``[lon1, lon2, lat1, lat2]``.
    :type area: Tuple[int, int, int, int]
    :param variables: Variables to be download. Check :class:`ERA5CONFIG` for valid values.
    :type variables: Union[Tuple[str, ...], str]
    :param save_path: Data save path.
    :type save_path: str
    :param product_type: Product type. Check :class:`ERA5CONFIG` for valid values.
    :type product_type: str
    :param data_format: Data format. Check :class:`ERA5CONFIG` for valid values.
    :type data_format: str
    :param dataset: Dataset type. Check :class:`ERA5CONFIG` for valid values.
    :type dataset: str
    :param download_format: Download format. Check :class:`ERA5CONFIG` for valid values.
    :type download_format: str
    :param pressure_level: Pressure levels to be download. Check :class:`ERA5CONFIG` for valid values.
    :type pressure_level: Union[int, List[int], str, List[str], None]
    :param overwrite: If the data file exists, force to download it when ``overwrite==True``.
    :type overwrite: bool
    :return: Data path.
    :rtype: str
    """
    global CDS_CLIENT

    # check variables and datasets
    if not _check_variables_and_datasets(variables, dataset):
        logger.error(f"Variables {variables} and dataset {dataset} doesn't correspond, check it")
        exit(1)

    # check if we need to create directory
    save_folder = dirname(save_path)
    if not exists(save_folder):
        makedirs(save_folder)

    # re-generate area tuple
    area = (area[-1], area[0], area[-2], area[1])

    # parse date
    if isinstance(date[0], str):
        date = [
            datetime.strptime(_date, "%Y-%m-%d %H:%M")  # type: ignore
            for _date in date
        ]
    year = list(set(_date.strftime("%Y") for _date in date))  # type: ignore
    month = list(set(_date.strftime("%m") for _date in date))  # type: ignore
    day = list(set(_date.strftime("%d") for _date in date))  # type: ignore
    time = list(set(_date.strftime("%H:%M") for _date in date))  # type: ignore

    # sort list
    year.sort()
    month.sort()
    day.sort()
    time.sort()

    # check if it exists
    if exists(save_path) and not overwrite:
        return save_path

    # create params dict
    params_dict = {
        "product_type": product_type,
        "data_format": data_format,
        "download_format": download_format,
        "variable": variables,
        "year": year,
        "month": month,
        "day": day,
        "time": time,
        "area": area,
    }

    # check if we need to add pressure_level to params dict
    if dataset == ERA5CONFIG.DATASET_ERA5_PRESSURE_LEVEL:
        if pressure_level is None:
            logger.error("You need to provide pressure levels to download data")
            exit(1)
        # convert value to str
        if not isinstance(pressure_level, list):
            pressure_level = [pressure_level]  # type: ignore
        if not isinstance(pressure_level[0], str):  # type: ignore
            pressure_level = [str(int(x)) for x in pressure_level]  # type: ignore
        # check
        if _check_pressure_level(pressure_level):  # type: ignore
            params_dict["pressure_level"] = pressure_level
        else:
            logger.error("You have passed wrong pressure level to download data, check it")
            exit(1)

    # download data
    logger.info(f"Downloading data to '{save_path}', it may take several tens of minutes, please wait...")

    if CDS_CLIENT is None:
        import cdsapi

        CDS_CLIENT = cdsapi.Client()

    CDS_CLIENT.retrieve(dataset, params_dict, save_path)

    return save_path


def prepare_wps_input_data(area: Tuple[int, int, int, int]):
    """
    Download essential data for WPS.

    :param area: Range of longitude and latitude, ``[lon1, lon2, lat1, lat2]``.
    :type area: Tuple[int, int, int, int]
    """
    wrf_config = WRFRUN.config.get_model_config("wrf")
    # get start and end date from config
    start_date = wrf_config["time"]["start_date"]
    end_date = wrf_config["time"]["end_date"]

    # remove second part
    start_date = start_date.strftime("%Y-%m-%d %H:%M")
    end_date = end_date.strftime("%Y-%m-%d %H:%M")

    # get hour step
    hour_step = wrf_config["time"]["input_data_interval"] // 3600

    # get data save path
    data_save_path = WRFRUN.config.get_input_data_path()

    # download data
    logger.info("Download background data of surface level...")
    download_data(
        start_date,
        end_date,
        hour_step,
        area,
        f"{data_save_path}/surface.grib",
        data_format="grib",
        data_type="surface",
        overwrite=True,
    )

    logger.info("Download background data of pressure level...")
    download_data(
        start_date,
        end_date,
        hour_step,
        area,
        f"{data_save_path}/pressure.grib",
        data_format="grib",
        data_type="pressure",
        overwrite=True,
    )

    # logger.info(f"Download NearGOOS data...")
    # download_data(start_date, end_date, hour_step, area,
    #               save_path=sst_save_path, data_type="goos", overwrite=True)


def download_data(
    start_date: str,
    end_date: str,
    hour_step: int,
    area: Tuple[int, int, int, int],
    save_path: str,
    data_format: Literal["nc", "grib"] = "nc",
    data_type: Literal["pressure", "surface"] = "pressure",
    overwrite=False,
) -> str:
    """
    Download essential data from ERA5.

    :param start_date: Begin date, for example, ``"2022-05-19 12:00"``.
    :type start_date: str
    :param end_date: End date, for example, ``"2022-05-22 18:00"``.
    :type end_date: str
    :param hour_step: Hour step.
    :type hour_step: int
    :param area: Range of longitude and latitude, ``[lon1, lon2, lat1, lat2]``.
    :type area: Tuple[int, int, int, int]
    :param save_path: Data save path.
    :type save_path: str
    :param data_format: Download data format. Default is ``"nc"``.
    :type data_format: Literal["nc", "grib"]
    :param data_type: Download data type. Default is ``"pressure"``.
    :param overwrite: If the data file exists, force to download it when ``overwrite==True``.
    :return: Data path.
    :rtype: str
    """
    # generate date list
    date_list = date_range(start_date, end_date, freq=f"{hour_step}H").strftime("%Y-%m-%d %H:%M").to_list()

    # check format
    if data_format == "nc":
        _data_format = ERA5CONFIG.FORMAT_NETCDF
    elif data_format == "grib":
        _data_format = ERA5CONFIG.FORMAT_GRIB
    else:
        logger.error(f"Wrong data format: {_data_format}")
        raise KeyError

    # check data type
    if data_type == "pressure":
        _data_type = ERA5CONFIG.DATASET_ERA5_PRESSURE_LEVEL
        variables = (
            ERA5CONFIG.VARIABLE_GEOPOTENTIAL,
            ERA5CONFIG.VARIABLE_RELATIVE_HUMIDITY,
            ERA5CONFIG.VARIABLE_SPECIFIC_HUMIDITY,
            ERA5CONFIG.VARIABLE_TEMPERATURE,
            ERA5CONFIG.VARIABLE_U_WIND,
            ERA5CONFIG.VARIABLE_V_WIND,
        )
        pressure_level = ERA5CONFIG.PRESSURE_LEVEL
    elif data_type == "surface":
        _data_type = ERA5CONFIG.DATASET_ERA5_SINGLE_LEVEL
        variables = (
            ERA5CONFIG.VARIABLE_SURFACE_PRESSURE,
            ERA5CONFIG.VARIABLE_MEAN_SEA_LEVEL_PRESSURE,
            ERA5CONFIG.VARIABLE_SKIN_TEMPERATURE,
            ERA5CONFIG.VARIABLE_2M_TEMPERATURE,
            ERA5CONFIG.VARIABLE_2M_DEWPOINT_TEMP,
            ERA5CONFIG.VARIABLE_10M_U_WIND,
            ERA5CONFIG.VARIABLE_10M_V_WIND,
            ERA5CONFIG.VARIABLE_LANDSEA_MASK,
            ERA5CONFIG.VARIABLE_SOIL_TEMP_LEVEL_1,
            ERA5CONFIG.VARIABLE_SOIL_TEMP_LEVEL_2,
            ERA5CONFIG.VARIABLE_SOIL_TEMP_LEVEL_3,
            ERA5CONFIG.VARIABLE_SOIL_TEMP_LEVEL_4,
            ERA5CONFIG.VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_1,
            ERA5CONFIG.VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_2,
            ERA5CONFIG.VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_3,
            ERA5CONFIG.VARIABLE_VOLUMETRIC_SOIL_WATER_LAYER_4,
            ERA5CONFIG.VARIABLE_SNOW_DEPTH,
            ERA5CONFIG.VARIABLE_SNOW_DENSITY,
        )
        pressure_level = None
    else:
        logger.error(f"Wrong data type: {_data_type}")
        raise KeyError

    # download data
    return find_era5_data(
        date=date_list,
        area=area,
        variables=variables,
        save_path=save_path,
        data_format=_data_format,
        dataset=_data_type,
        pressure_level=pressure_level,
        download_format=ERA5CONFIG.DOWNLOAD_UNZIP,
        overwrite=overwrite,
    )


__all__ = ["find_era5_data", "ERA5CONFIG", "download_data", "prepare_wps_input_data"]
