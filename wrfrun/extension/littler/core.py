"""
wrfrun.extension.littler.core
#############################

Implementation of ``extension.littler``'s core functionality.

.. autosummary::
    :toctree: generated/

    to_fstring
    LittleRHead
    LittleRData
    LittleR
"""

from json import loads, dumps
from typing import Union, Tuple, Iterable
from zipfile import ZipFile

from pandas import DataFrame, read_csv
import numpy as np

from wrfrun.core import WRFRUNConfig
from wrfrun.utils import logger


def to_fstring(var: Union[int, float, bool, str], length: Union[int, Tuple[int, int]]) -> str:
    """
    Convert a basic variable to a string following the Fortran standard.

    Convert a float number to a string of length 7 with 3 decimal places:

    >>> to_fstring(0.1, (7, 3))
    '  0.100'

    Convert an integer to a string of length 3:

    >>> to_fstring(1, 3)
    '  1'

    Convert a boolean value to a string of length 4:
    >>> to_fstring(True, 4)
    '   T'

    :param var: Basic variable that can be one of the ``[int, float, bool, str]``.
    :type var: Union[int, float, bool, str]
    :param length: The length of the output string. If the type of ``var`` is ``float``,
                   the length must contain two parameters ``(total length, decimal length)``.
    :type length: Union[int, Tuple[int, int]]
    :return: Converted string.
    :rtype: str
    """
    if isinstance(var, float):
        if not isinstance(length, tuple):
            logger.error(
                "`length` must be a tuple contain two values `(total length, decimal length)` when `var` is `float`"
            )
            raise ValueError(
                "`length` must be a tuple contain two values `(total length, decimal length)` when `var` is `float`"
            )

        res = f"{var:{length[0]}.{length[1]}f}"

    else:
        if not isinstance(length, int):
            logger.error(
                "`length` must be an int value when `var` is not `float`"
            )
            raise ValueError(
                "`length` must be an int value when `var` is not `float`"
            )

        if isinstance(var, bool):
            res = "T" if var else "F"
            res = res.rjust(length, " ")

        else:
            res = f"{var:{length}}"

    return res


class LittleRHead(dict):
    """
    Headers of LITTLE_R observation data.
    """
    def __init__(
        self,
        longitude: float,
        latitude: float,
        fm: str,
        elevation: float,
        is_bogus: bool,
        date: str,
        ID="-----",
        name="wrfrun",
        source="Created by wrfrun package",
        num_sequence=0,
        sea_level_pressure=-888888,
        reference_pressure=-888888,
        surface_pressure=-888888,
        cloud_cover=-888888,
        precipitable_water=-888888,
        quality_control: Union[dict, int] = 0,
        **kwargs
    ) -> None:
        """
        Headers of LITTLE_R observation data.

        :param longitude: Longitude.
        :type longitude: float
        :param latitude: Latitude.
        :type latitude: float
        :param fm: Platform code (FM-Code). Here is the list of `Valid FM Codes <https://www2.mmm.ucar.edu/wrf/users/wrfda/OnlineTutorial/Help/littler.html#FM>`_.
        :type fm: str
        :param elevation: Elevation.
        :type elevation: float
        :param is_bogus: Is bogus?
        :type is_bogus: bool
        :param date: Date string in format ``%Y%m%d%H%M%S``, UTC time.
        :type date: str
        :param ID: ID, defaults to "-----".
        :type ID: str
        :param name: Name, defaults to "wrfrun".
        :type name: str
        :param source: Data source, defaults to "Created by wrfrun package".
        :type source: str
        :param num_sequence: Sequence number which is used to merge multiple record data, the less the num is, the newer the data is. Defaults to 0.
        :type num_sequence: int
        :param sea_level_pressure: Sea level pressure. Defaults to -888,888.
        :type sea_level_pressure: int
        :param reference_pressure: Reference pressure. Defaults to -888,888.
        :type reference_pressure: int
        :param surface_pressure: Surface pressure. Defaults to -888,888.
        :type surface_pressure: int
        :param cloud_cover: Cloud cover. Defaults to -888,888.
        :type cloud_cover: int
        :param precipitable_water: Precipitable water. Defaults to -888,888.
        :type precipitable_water: int
        :param quality_control: Quality control flag for observation data that can be specified per data in a dict. Defaults to 0.
        :type quality_control: Union[dict, int]
        """
        super().__init__(
            longitude=longitude,
            latitude=latitude,
            fm=fm,
            elevation=elevation,
            is_bogus=is_bogus,
            date=date,
            ID=ID,
            name=name,
            source=source,
            num_sequence=num_sequence,
            sea_level_pressure=sea_level_pressure,
            reference_pressure=reference_pressure,
            surface_pressure=surface_pressure,
            cloud_cover=cloud_cover,
            precipitable_water=precipitable_water,
            quality_control=quality_control,
            num_valid_field=256,
            num_error=-888888,
            num_warning=-888888,
            num_duplicate=-888888,
            is_sounding=True,
            discard=False,
            time=-888888,
            julian_day=-888888,
            ground_temperature=-888888,
            sst=-888888,
            precipitation=-888888,
            temp_daily_max=-888888,
            temp_daily_min=-888888,
            temp_night_min=-888888,
            pressure_delta_3h=-888888,
            pressure_delta_24h=-888888,
            ceiling=-888888,
        )
        self.longitude = longitude
        self.latitude = latitude
        self.fm = fm
        self.elevation = elevation
        self.is_bogus = is_bogus
        self.date = date
        self.ID = ID
        self.name = name
        self.source = source
        self.num_sequence = num_sequence
        self.sea_level_pressure = sea_level_pressure
        self.reference_pressure = reference_pressure
        self.surface_pressure = surface_pressure
        self.cloud_cover = cloud_cover
        self.precipitable_water = precipitable_water
        self.quality_control = quality_control

        # other unused field
        self.num_valid_field = 256
        self.num_error = -888888
        self.num_warning = -888888
        self.num_duplicate = -888888
        self.is_sounding = True
        self.discard = False
        self.time = -888888
        self.julian_day = -888888
        self.ground_temperature = -888888
        self.sst = -888888
        self.precipitation = -888888
        self.temp_daily_max = -888888
        self.temp_daily_min = -888888
        self.temp_night_min = -888888
        self.pressure_delta_3h = -888888
        self.pressure_delta_24h = -888888
        self.ceiling = -888888

        _ = kwargs

    def __str__(self) -> str:
        return self._convert_to_fstring()

    # def __repr__(self) -> str:
    #     return self._convert_to_fstring()

    def _convert_to_fstring(self) -> str:
        return f"{self.latitude:20.5f}" \
               f"{self.longitude:20.5f}" \
               f"{self.ID.rjust(40, ' ')}" \
               f"{self.name.rjust(40, ' ')}" \
               f"{self.fm.rjust(40, ' ')}" \
               f"{self.source.rjust(40, ' ')}" \
               f"{self.elevation:20.5f}" \
               f"{self.num_valid_field:10d}" \
               f"{self.num_error:10d}" \
               f"{self.num_warning:10d}" \
               f"{self.num_sequence:10d}" \
               f"{self.num_duplicate:10d}" \
               f"{to_fstring(self.is_sounding, 10)}" \
               f"{to_fstring(self.is_bogus, 10)}" \
               f"{to_fstring(self.discard, 10)}" \
               f"{self.time:10d}" \
               f"{self.julian_day:10d}" \
               f"{self.date.rjust(20, ' ')}" + self._generate_data_qc()

    def _generate_data_qc(self) -> str:
        field = [
            "sea_level_pressure",
            "reference_pressure",
            "ground_temperature",
            "sst",
            "surface_pressure",
            "precipitation",
            "temp_daily_max",
            "temp_daily_min",
            "temp_night_min",
            "pressure_delta_3h",
            "pressure_delta_24h",
            "cloud_cover",
            "ceiling",
            "precipitable_water",
        ]

        if isinstance(self.quality_control, int):
            res = ""
            for key in field:
                res += f"{getattr(self, key):13.5f}{self.quality_control:7d}"
        else:
            res = ""
            for key in field:
                res += f"{getattr(self, key):13.5f}{self.quality_control[key]:7d}"

        return res


LITTLE_R_DATA_FIELD = [
    "pressure", "pressure_qc",
    "height", "height_qc",
    "temperature", "temperature_qc",
    "dew_point", "dew_point_qc",
    "wind_speed", "wind_speed_qc",
    "wind_direction", "wind_direction_qc",
    "wind_u", "wind_u_qc",
    "wind_v", "wind_v_qc",
    "relative_humidity", "relative_humidity_qc",
    "thickness", "thickness_qc",
]


class LittleRData(DataFrame):
    """
    LITTLE_R observation data without headers.
    """
    def __init__(
        self,
        data=None,
        index=None,
        columns=None,
        pressure: Union[Iterable, float] = 100000.,
        height: Union[Iterable, float] = -888888.,
        temperature: Union[Iterable, float] = 264.,
        dew_point: Union[Iterable, float] = 263.,
        wind_speed: Union[Iterable, float] = -888888.,
        wind_direction: Union[Iterable, float] = -888888.,
        wind_u: Union[Iterable, float] = -888888.,
        wind_v: Union[Iterable, float] = -888888.,
        relative_humidity: Union[Iterable, float] = -888888.,
        thickness: Union[Iterable, float] = -888888.,
        quality_control_flag: Union[Iterable, dict, int] = 0,
        **kwargs
    ) -> None:
        """
        LITTLE_R observation data without headers.

        :class:`LittleRData` inherits from ``pandas.DataFrame``, so you have two ways to create a ``LittleRData`` instance:

        1. Create instance like normal ``pandas.DataFrame`` instance:

        >>> obs_data = {
        ...     "pressure": [100000., 90000.],
        ...     "pressure_qc": [0, 0],
        ...     "height": [-888888., -888888.],
        ...     "height_qc": [0, 0],
        ...     "temperature": [264., 260.],
        ...     "temperature_qc": [0, 0],
        ...     "dew_point": [263., 255.],
        ...     "dew_point_qc": [0, 0],
        ...     "wind_speed": [-888888., -888888.],
        ...     "wind_speed_qc": [0, 0],
        ...     "wind_direction": [-888888., -888888.],
        ...     "wind_direction_qc": [0, 0],
        ...     "wind_u": [-888888., -888888.],
        ...     "wind_u_qc": [0, 0],
        ...     "wind_v": [-888888., -888888.],
        ...     "wind_v_qc": [0, 0],
        ...     "relative_humidity": [-888888., -888888.],
        ...     "relative_humidity_qc": [0, 0],
        ...     "thickness": [-888888., -888888.],
        ...     "thickness_qc": [0, 0],
        ... }
        >>> littler_data = LittleRData(data=data)

        However, you need to give all quality control flags, and make sure the ``data`` has all essential valus.

        2. Create instance by giving each value one after another

        >>> obs_data = LittleRData(
        ...     pressure=[100000., 90000.],
        ...     height=[-888888., -888888.],
        ...     temperature=[264., 260.],
        ...     dew_point=[263., 255.],
        ...     wind_speed=[-888888., -888888.],
        ...     wind_direction=[-888888., -888888.],
        ...     wind_u=[-888888., -888888.],
        ...     wind_v=[-888888., -888888.],
        ...     relative_humidity=[-888888., -888888.],
        ...     thickness=[-888888., -888888.],
        ...     quality_control_flag=[0, 0],
        ... )

        In this way, you can set all quality control flag of one pressure level by giving ``quality_control_flag``.

        If you want to set an invalid value, **USE -888888**.

        To generate a LITTLE_R format record, just use :func:`str`

        >>> str(obs_data)

        :param data: This argument is passed to ``pandas.DataFrame`` directly.
        :type data: ndarray | Iterable | dict | DataFrame
        :param index: This argument is passed to ``pandas.DataFrame`` directly.
        :type index: Index or array-like
        :param columns: This argument is passed to ``pandas.DataFrame`` directly.
        :type columns: Index or array-like
        :param pressure: Pressure in ``Pa``. Default is 100000 Pa.
        :type pressure: float | Iterable
        :param height: Elevation in ``meter``. Default is -888888.
        :type height: float | Iterable
        :param temperature: Air temperature in ``K``. Default is 264 K.
        :type temperature: float | Iterable
        :param dew_point: Dew point temperature in ``K``. Default is 263 K.
        :type dew_point: float | Iterable
        :param wind_speed: Wind speed in ``meter / seconds``. Default is -888888.
        :type wind_speed: float | Iterable
        :param wind_direction: Wind direction in ``degree``, 0/360 represents the north. Default is -888888.
        :type wind_direction: float | Iterable
        :param wind_u: East-west wind speed in ``meter / seconds``. Default is -888888.
        :type wind_u: float | Iterable
        :param wind_v: North-south wind speed in ``meter / seconds``. Default is -888888.
        :type wind_v: float | Iterable
        :param relative_humidity: Relative humidity in ``percentage``. Default is -888888.
        :type relative_humidity: float | Iterable
        :param thickness: Thickness in ``meter``. Default is -888888.
        :type thickness: float | Iterable
        :param quality_control_flag: Quality control flag for all data or data in the same line.
                                     This argument can only be ``0``, ``1`` or array-like object which only contains 0 or 1.
                                     ``0`` means no quality control, ``1`` means having quality control. Default is 0.
        :type quality_control_flag: int | Iterable
        :param kwargs: Other keyword arguments passed to parent class.
        :type kwargs: dict
        """
        # check data type
        if data is not None:
            super().__init__(data=data, index=index, columns=columns, **kwargs)  # type: ignore

        else:
            if isinstance(pressure, float):
                pressure = np.array([pressure]).astype(float)
                height = np.array([height]).astype(float)
                temperature = np.array([temperature]).astype(float)
                dew_point = np.array([dew_point]).astype(float)
                wind_speed = np.array([wind_speed]).astype(float)
                wind_direction = np.array([wind_direction]).astype(float)
                wind_u = np.array([wind_u]).astype(float)
                wind_v = np.array([wind_v]).astype(float)
                relative_humidity = np.array([relative_humidity]).astype(float)
                thickness = np.array([thickness]).astype(float)
                quality_control_flag = np.array(
                    [quality_control_flag]
                ).astype(int)
            else:
                pressure = np.asarray(pressure).astype(float)
                height = np.asarray(height).astype(float)
                temperature = np.asarray(temperature).astype(float)
                dew_point = np.asarray(dew_point).astype(float)
                wind_speed = np.asarray(wind_speed).astype(float)
                wind_direction = np.asarray(wind_direction).astype(float)
                wind_u = np.asarray(wind_u).astype(float)
                wind_v = np.asarray(wind_v).astype(float)
                relative_humidity = np.asarray(relative_humidity).astype(float)
                thickness = np.asarray(thickness).astype(float)
                quality_control_flag = np.asarray(
                    quality_control_flag
                ).astype(int)

            # construct data
            if isinstance(quality_control_flag, dict):
                data = {
                    "pressure": pressure,
                    "pressure_qc": quality_control_flag["pressure"],
                    "height": height,
                    "height_qc": quality_control_flag["height"],
                    "temperature": temperature,
                    "temperature_qc": quality_control_flag["temperature"],
                    "dew_point": dew_point,
                    "dew_point_qc": quality_control_flag["dew_point"],
                    "wind_speed": wind_speed,
                    "wind_speed_qc": quality_control_flag["wind_speed"],
                    "wind_direction": wind_direction,
                    "wind_direction_qc": quality_control_flag["wind_direction"],
                    "wind_u": wind_u,
                    "wind_u_qc": quality_control_flag["wind_u"],
                    "wind_v": wind_v,
                    "wind_v_qc": quality_control_flag["wind_v"],
                    "relative_humidity": relative_humidity,
                    "relative_humidity_qc": quality_control_flag["relative_humidity"],
                    "thickness": thickness,
                    "thickness_qc": quality_control_flag["thickness"],
                }
            else:
                data = {
                    "pressure": pressure,
                    "pressure_qc": quality_control_flag,
                    "height": height,
                    "height_qc": quality_control_flag,
                    "temperature": temperature,
                    "temperature_qc": quality_control_flag,
                    "dew_point": dew_point,
                    "dew_point_qc": quality_control_flag,
                    "wind_speed": wind_speed,
                    "wind_speed_qc": quality_control_flag,
                    "wind_direction": wind_direction,
                    "wind_direction_qc": quality_control_flag,
                    "wind_u": wind_u,
                    "wind_u_qc": quality_control_flag,
                    "wind_v": wind_v,
                    "wind_v_qc": quality_control_flag,
                    "relative_humidity": relative_humidity,
                    "relative_humidity_qc": quality_control_flag,
                    "thickness": thickness,
                    "thickness_qc": quality_control_flag,
                }

            super().__init__(data=data)  # type: ignore

    @classmethod
    def from_csv(cls, csv_path: str):
        """
        Read saved LITTLE_R data from a CSV file.

        :param csv_path: CSV file path.
        :type csv_path: str
        :return: ``LittleRData`` instance.
        :rtype: LittleRData
        """
        data_dict = read_csv(csv_path).to_dict()
        return cls.from_dict(data_dict)

    @classmethod
    def from_dict(cls, data: dict, orient='columns', dtype=None, columns=None):
        """
        Create ``LittleRData`` instance from a dict.
        This method inspects all fields in ``data`` and supplements any missing fields with invalid value (-888888).

        :param data: A dict contains all data.
        :type data: dict
        :param orient: This argument is passed to ``DataFrame.from_dict`` directly.
        :type orient: str
        :param dtype: This argument is passed to ``DataFrame.from_dict`` directly.
        :type dtype: dtype
        :param columns: This argument is passed to ``DataFrame.from_dict`` directly.
        :type columns: Index or array-like
        :return: ``LittleRData`` instance.
        :rtype: LittleRData
        """
        # check fields
        data_key = next(iter(data))
        temp_data = data[data_key]
        for field in LITTLE_R_DATA_FIELD:
            if field not in data:
                if field.endswith("_qc"):
                    data[field] = np.zeros_like(temp_data).astype(int)
                else:
                    data[field] = np.zeros_like(temp_data) - 888888.

        return super().from_dict(data, orient, dtype, columns)  # type: ignore

    def __str__(self) -> str:
        return self._convert_to_fstring()

    def _convert_to_fstring(self) -> str:
        fields = [
            "pressure",
            "height",
            "temperature",
            "dew_point",
            "wind_speed",
            "wind_direction",
            "wind_u",
            "wind_v",
            "relative_humidity",
            "thickness",
        ]
        qc_fields = [
            "pressure_qc",
            "height_qc",
            "temperature_qc",
            "dew_point_qc",
            "wind_speed_qc",
            "wind_direction_qc",
            "wind_u_qc",
            "wind_v_qc",
            "relative_humidity_qc",
            "thickness_qc",
        ]

        res = ""
        valid_field_num = 0
        for row in self.index:
            for (key, qc_key) in zip(fields, qc_fields):
                _field = self.loc[row, key]
                _field_qc = self.loc[row, qc_key]

                if _field > -100:  # type: ignore
                    valid_field_num += 1

                res += f"{_field:13.5f}{_field_qc:7d}"
            res += "\n"

        # add ending record
        for (_, _) in zip(fields, qc_fields):
            res += f"{-777777:13.5f}{0:7d}"
        res += "\n"

        # add tail integers
        res += f"{valid_field_num:7d}{0:7d}{0:7d}"

        return res


class LittleR(LittleRData):
    """
    Manage LITTLE_R observation data.
    """

    _metadata = ["little_r_head"]

    def __init__(
        self,
        data=None,
        index=None,
        columns=None,
        data_header: Union[dict, None] = None,
        pressure: Union[Iterable, float] = 100000.,
        height: Union[Iterable, float] = -888888.,
        temperature: Union[Iterable, float] = 264.,
        dew_point: Union[Iterable, float] = 263.,
        wind_speed: Union[Iterable, float] = -888888.,
        wind_direction: Union[Iterable, float] = -888888.,
        wind_u: Union[Iterable, float] = -888888.,
        wind_v: Union[Iterable, float] = -888888.,
        relative_humidity: Union[Iterable, float] = -888888.,
        thickness: Union[Iterable, float] = -888888.,
        quality_control_flag: Union[Iterable, dict, int] = 0,
        **kwargs
    ) -> None:
        """
        ``LittleR`` class helps you manage LITTLE_R data easily.
        You can create a ``LittleR`` instance with your observation data,
        then generate LITTLE_R format record or save all data to a **Zipped Little R** file (ends with ``.zlr``).

        **Zipped Little R** file is a compressed file having two parts: ``header`` and ``data``.
        ``header`` is a JSON file that stores LITTLE_R file header,
        and ``data`` is a CSV file that stores record data.
        You can even create ``.zlr`` file with other programs and read the file using ``LittleR``,
        as long as it has all essential data.

        1. Constructing LittleR from a dictionary

        >>> obs_data = {
        ...     "pressure": [100000., 90000.],
        ...     "pressure_qc": [0, 0],
        ...     "height": [-888888., -888888.],
        ...     "height_qc": [0, 0],
        ...     "temperature": [264., 260.],
        ...     "temperature_qc": [0, 0],
        ...     "dew_point": [263., 255.],
        ...     "dew_point_qc": [0, 0],
        ...     "wind_speed": [-888888., -888888.],
        ...     "wind_speed_qc": [0, 0],
        ...     "wind_direction": [-888888., -888888.],
        ...     "wind_direction_qc": [0, 0],
        ...     "wind_u": [-888888., -888888.],
        ...     "wind_u_qc": [0, 0],
        ...     "wind_v": [-888888., -888888.],
        ...     "wind_v_qc": [0, 0],
        ...     "relative_humidity": [-888888., -888888.],
        ...     "relative_humidity_qc": [0, 0],
        ...     "thickness": [-888888., -888888.],
        ...     "thickness_qc": [0, 0],
        ... }
        >>> obs_header = {
        ...     "longitude": 120,
        ...     "latitude": 60,
        ...     "fm": "FM-19",
        ...     "elevation": 0,
        ...     "is_bogus": True,
        ...     "date": "20250902070000"
        ...}
        >>> littler_data = LittleR(data=data, data_header=obs_header)

        You can set header after constructing LittleR

        >>> obs_data = {
        ...     "pressure": [100000., 90000.],
        ...     "pressure_qc": [0, 0],
        ...     "height": [-888888., -888888.],
        ...     "height_qc": [0, 0],
        ...     "temperature": [264., 260.],
        ...     "temperature_qc": [0, 0],
        ...     "dew_point": [263., 255.],
        ...     "dew_point_qc": [0, 0],
        ...     "wind_speed": [-888888., -888888.],
        ...     "wind_speed_qc": [0, 0],
        ...     "wind_direction": [-888888., -888888.],
        ...     "wind_direction_qc": [0, 0],
        ...     "wind_u": [-888888., -888888.],
        ...     "wind_u_qc": [0, 0],
        ...     "wind_v": [-888888., -888888.],
        ...     "wind_v_qc": [0, 0],
        ...     "relative_humidity": [-888888., -888888.],
        ...     "relative_humidity_qc": [0, 0],
        ...     "thickness": [-888888., -888888.],
        ...     "thickness_qc": [0, 0],
        ... }
        >>> littler_data = LittleR(data=data)
        >>> littler_data.set_header(longitude=120, latitude=60, fm="FM-19", elevation=0, is_bogus=True, date="20250902070000")

        2. Constructing LittleR by giving observation data one by one

        >>> littler_data = LittleR(
        ...     pressure=[100000., 90000.],
        ...     height=[-888888., -888888.],
        ...     temperature=[264., 260.],
        ...     dew_point=[263., 255.],
        ...     wind_speed=[-888888., -888888.],
        ...     wind_direction=[-888888., -888888.],
        ...     wind_u=[-888888., -888888.],
        ...     wind_v=[-888888., -888888.],
        ...     relative_humidity=[-888888., -888888.],
        ...     thickness=[-888888., -888888.],
        ...     quality_control_flag=[0, 0],
        ...)

        3. Constructing LittleR by reading ``.zlr`` file

        >>> zlr_file_path = "data/test.zlr"
        >>> littler_data = LittleR.from_zlr(zlr_file_path)

        4. Generating LITTLE_R format record

        >>> str(littler_data)

        5. Saving data to ``.zlr`` file

        >>> littler_data.to_zlr("data/test.zlr")

        :param data: This argument is passed to ``pandas.DataFrame`` directly.
        :type data: ndarray | Iterable | dict | DataFrame
        :param index: This argument is passed to ``pandas.DataFrame`` directly.
        :type index: Index or array-like
        :param columns: This argument is passed to ``pandas.DataFrame`` directly.
        :type columns: Index or array-like
        :param data_header: A dict contains LITTLE_R headers.
        :type data_header: dict
        :param pressure: Pressure in ``Pa``. Default is 100000 Pa.
        :type pressure: float | Iterable
        :param height: Elevation in ``meter``. Default is -888888.
        :type height: float | Iterable
        :param temperature: Air temperature in ``K``. Default is 264 K.
        :type temperature: float | Iterable
        :param dew_point: Dew point temperature in ``K``. Default is 263 K.
        :type dew_point: float | Iterable
        :param wind_speed: Wind speed in ``meter / seconds``. Default is -888888.
        :type wind_speed: float | Iterable
        :param wind_direction: Wind direction in ``degree``, 0/360 represents the north. Default is -888888.
        :type wind_direction: float | Iterable
        :param wind_u: East-west wind speed in ``meter / seconds``. Default is -888888.
        :type wind_u: float | Iterable
        :param wind_v: North-south wind speed in ``meter / seconds``. Default is -888888.
        :type wind_v: float | Iterable
        :param relative_humidity: Relative humidity in ``percentage``. Default is -888888.
        :type relative_humidity: float | Iterable
        :param thickness: Thickness in ``meter``. Default is -888888.
        :type thickness: float | Iterable
        :param quality_control_flag: Quality control flag for all data or data in the same line.
                                     This argument can only be ``0``, ``1`` or array-like object which only contains 0 or 1.
                                     ``0`` means no quality control, ``1`` means having quality control. Default is 0.
        :type quality_control_flag: int | Iterable
        :param kwargs: Other keyword arguments passed to parent class.
        :type kwargs: dict
        """
        super().__init__(
            data=data,
            pressure=pressure,
            height=height,
            temperature=temperature,
            dew_point=dew_point,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            wind_u=wind_u,
            wind_v=wind_v,
            relative_humidity=relative_humidity,
            thickness=thickness,
            quality_control_flag=quality_control_flag,
            index=index,
            columns=columns,
            **kwargs
        )

        if data_header is None:
            self.little_r_head = None
        else:
            self.little_r_head = LittleRHead(**data_header)

    def set_header(
        self,
        longitude: float,
        latitude: float,
        fm: str,
        elevation: float,
        is_bogus: bool,
        date: str,
        ID="-----",
        name="wrfrun",
        source="Created by wrfrun package",
        num_sequence=0,
        sea_level_pressure=-888888,
        reference_pressure=-888888,
        surface_pressure=-888888,
        cloud_cover=-888888,
        precipitable_water=-888888,
        quality_control: Union[dict, int] = 0,
        **kwargs
    ):
        """
        Set headers of LITTLE_R observation data.

        :param longitude: Longitude.
        :type longitude: float
        :param latitude: Latitude.
        :type latitude: float
        :param fm: Platform code (FM-Code).
                   Here is the list of `Valid FM Codes <https://www2.mmm.ucar.edu/wrf/users/wrfda/OnlineTutorial/Help/littler.html#FM>`_.
        :type fm: str
        :param elevation: Elevation.
        :type elevation: float
        :param is_bogus: Is bogus?
        :type is_bogus: bool
        :param date: Date string in format ``%Y%m%d%H%M%S``, UTC time.
        :type date: str
        :param ID: ID, defaults to "-----".
        :type ID: str, optional
        :param name: Name, defaults to "wrfrun".
        :type name: str, optional
        :param source: Data source, defaults to "Created by wrfrun package".
        :type source: str, optional
        :param num_sequence: Sequence number, used to merge multiple record data, the less the num is, the newer the data is, defaults to 0
        :type num_sequence: int, optional
        :param sea_level_pressure: Sea level pressure, defaults to -888888
        :type sea_level_pressure: int, optional
        :param reference_pressure: Reference pressure, defaults to -888888
        :type reference_pressure: int, optional
        :param surface_pressure: Surface pressure, defaults to -888888
        :type surface_pressure: int, optional
        :param cloud_cover: Cloud cover, defaults to -888888
        :type cloud_cover: int, optional
        :param precipitable_water: Precipitable water, defaults to -888888
        :type precipitable_water: int, optional
        :param quality_control: Quality control flag for observation data, can be specified per data in a dict, defaults to 0
        :type quality_control: Union[dict, int], optional
        """
        self.little_r_head = LittleRHead(
            longitude, latitude, fm, elevation, is_bogus, date, ID,
            name=name, source=source, num_sequence=num_sequence, sea_level_pressure=sea_level_pressure, reference_pressure=reference_pressure,
            surface_pressure=surface_pressure, cloud_cover=cloud_cover, precipitable_water=precipitable_water, quality_control=quality_control,
            **kwargs
        )

    def __str__(self) -> str:
        data_str = super().__str__()
        return f"{str(self.little_r_head)}\n{data_str}"

    @classmethod
    def from_csv(cls, csv_path: str):
        """
        Read observation data from CSV file.

        :param csv_path: CSV file path.
        :type csv_path: str
        :return: ``LittleR`` instance.
        :rtype: LittleR
        """
        return super().from_csv(csv_path)

    def to_zlr(self, file_path: str):
        """
        Save all LittleR data to Zipped Little R file.

        :param file_path: File save path.
        :type file_path: str
        """
        if not file_path.endswith(".zlr"):
            file_path = f"{file_path}.zlr"

        file_path = WRFRUNConfig.parse_resource_uri(file_path)

        with ZipFile(file_path, "w") as zip_file:
            with zip_file.open("header", "w") as header_file:
                header_file.write(dumps(self.little_r_head).encode())

            with zip_file.open("data", "w") as data_file:
                self.to_csv(data_file, index=False)

    @classmethod
    def from_zlr(cls, file_path: str):
        """
        Read data from a ".zlr" file.

        :param file_path: The file path.
        :type file_path: str
        :return: ``LittleR`` instance.
        :rtype: LittleR
        """
        file_path = WRFRUNConfig.parse_resource_uri(file_path)

        with ZipFile(file_path, "r") as zip_file:
            with zip_file.open("header", "r") as header_file:
                header = loads(header_file.read().decode())

            with zip_file.open("data", "r") as data_file:
                little_r = cls.from_csv(data_file)  # type: ignore

        little_r.set_header(**header)  # type: ignore

        return little_r


__all__ = ["LittleRHead", "LittleRData", "LittleR"]
