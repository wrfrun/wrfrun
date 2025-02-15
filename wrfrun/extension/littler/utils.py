from json import loads, dumps
from typing import Union, Tuple
from zipfile import ZipFile

from pandas import DataFrame, read_csv
import numpy as np

from wrfrun.utils import logger


def to_fstring(var: Union[int, float, bool, str], length: Union[int, Tuple[int, int]]) -> str:
    """Convert a basic variable to a string following the Fortran standard.

    :param var: Basic variable, can be one of the ``[int, float, bool, str]``.
    :type var: Union[int, float, bool, str]
    :param length: The length of the output string. 
        If the type of ``var`` is ``float``, the length must contain two parameters ``(total length, decimal length)``.
    :type length: Union[int, Tuple[int, int]]
    :return: Converted string.
    :rtype: str
    """
    if isinstance(var, float):
        if not isinstance(length, tuple):
            logger.error(
                f"`length` must be a tuple contain two values `(total length, decimal length)` when `var` is `float`")
            raise ValueError(
                f"`length` must be a tuple contain two values `(total length, decimal length)` when `var` is `float`")

        res = f"{var:{length[0]}.{length[1]}}"

    else:
        if not isinstance(length, int):
            logger.error(
                f"`length` must be an int value when `var` is not `float`")
            raise ValueError(
                f"`length` must be an int value when `var` is not `float`")

        if isinstance(var, bool):
            res = "T" if var else "F"
            res = res.rjust(length, " ")

        else:
            res = f"{var:{length}}"

    return res


class LittleRHead(dict):
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
        """Head info of little_r obs data.

        :param longitude: Longitude.
        :type longitude: float
        :param latitude: Latitude.
        :type latitude: float
        :param fm: Platform code (FM-Code).
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
        super().__init__(
            longitude = longitude,
            latitude = latitude,
            fm = fm,
            elevation = elevation,
            is_bogus = is_bogus,
            date = date,
            ID = ID,
            name = name,
            source = source,
            num_sequence = num_sequence,
            sea_level_pressure = sea_level_pressure,
            reference_pressure = reference_pressure,
            surface_pressure = surface_pressure,
            cloud_cover = cloud_cover,
            precipitable_water = precipitable_water,
            quality_control = quality_control,
            num_valid_field = 256,
            num_error = -888888,
            num_warning = -888888,
            num_duplicate = -888888,
            is_sounding = True,
            discard = False,
            time = -888888,
            julian_day = -888888,
            ground_temperature = -888888,
            sst = -888888,
            precipitation = -888888,
            temp_daily_max = -888888,
            temp_daily_min = -888888,
            temp_night_min = -888888,
            pressure_delta_3h = -888888,
            pressure_delta_24h = -888888,
            ceiling = -888888,
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
        return f"{self.latitude:20.5f}"  \
            f"{self.longitude:20.5f}"  \
            f"{self.ID.rjust(40, ' ')}"  \
            f"{self.name.rjust(40, ' ')}"  \
            f"{self.fm.rjust(40, ' ')}"  \
            f"{self.source.rjust(40, ' ')}"  \
            f"{self.elevation:20.5f}"  \
            f"{self.num_valid_field:10d}"  \
            f"{self.num_error:10d}"  \
            f"{self.num_warning:10d}"  \
            f"{self.num_sequence:10d}"  \
            f"{self.num_duplicate:10d}"  \
            f"{to_fstring(self.is_sounding, 10)}"  \
            f"{to_fstring(self.is_bogus, 10)}"  \
            f"{to_fstring(self.discard, 10)}"  \
            f"{self.time:10d}"  \
            f"{self.julian_day:10d}"  \
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
    def __init__(
        self,
        data=None,
        index=None,
        columns=None,
        pressure: Union[np.ndarray, float] = 100000.,
        height: Union[np.ndarray, float] = -888888.,
        temperature: Union[np.ndarray, float] = 264.,
        dew_point: Union[np.ndarray, float] = 263.,
        wind_speed: Union[np.ndarray, float] = -888888.,
        wind_direction: Union[np.ndarray, float] = -888888.,
        wind_u: Union[np.ndarray, float] = -888888.,
        wind_v: Union[np.ndarray, float] = -888888.,
        relative_humidity: Union[np.ndarray, float] = -888888.,
        thickness: Union[np.ndarray, float] = -888888.,
        qulity_control_flag: Union[np.ndarray, dict, int] = 0,
        **kwargs
    ) -> None:
        # check data type
        if data is not None:
            super().__init__(data=data, index=index, columns=columns, **kwargs)   # type: ignore

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
                qulity_control_flag = np.array(
                    [qulity_control_flag]).astype(int)
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
                qulity_control_flag = np.asarray(
                    qulity_control_flag).astype(int)

            # construct data
            if isinstance(qulity_control_flag, dict):
                data = {
                    "pressure": pressure,
                    "pressure_qc": qulity_control_flag["pressure"],
                    "height": height,
                    "height_qc": qulity_control_flag["height"],
                    "temperature": temperature,
                    "temperature_qc": qulity_control_flag["temperature"],
                    "dew_point": dew_point,
                    "dew_point_qc": qulity_control_flag["dew_point"],
                    "wind_speed": wind_speed,
                    "wind_speed_qc": qulity_control_flag["wind_speed"],
                    "wind_direction": wind_direction,
                    "wind_direction_qc": qulity_control_flag["wind_direction"],
                    "wind_u": wind_u,
                    "wind_u_qc": qulity_control_flag["wind_u"],
                    "wind_v": wind_v,
                    "wind_v_qc": qulity_control_flag["wind_v"],
                    "relative_humidity": relative_humidity,
                    "relative_humidity_qc": qulity_control_flag["relative_humidity"],
                    "thickness": thickness,
                    "thickness_qc": qulity_control_flag["thickness"],
                }
            else:
                data = {
                    "pressure": pressure,
                    "pressure_qc": qulity_control_flag,
                    "height": height,
                    "height_qc": qulity_control_flag,
                    "temperature": temperature,
                    "temperature_qc": qulity_control_flag,
                    "dew_point": dew_point,
                    "dew_point_qc": qulity_control_flag,
                    "wind_speed": wind_speed,
                    "wind_speed_qc": qulity_control_flag,
                    "wind_direction": wind_direction,
                    "wind_direction_qc": qulity_control_flag,
                    "wind_u": wind_u,
                    "wind_u_qc": qulity_control_flag,
                    "wind_v": wind_v,
                    "wind_v_qc": qulity_control_flag,
                    "relative_humidity": relative_humidity,
                    "relative_humidity_qc": qulity_control_flag,
                    "thickness": thickness,
                    "thickness_qc": qulity_control_flag,
                }

            super().__init__(data=data)    # type: ignore

    @classmethod
    def from_csv(cls, csv_path):
        data_dict = read_csv(csv_path).to_dict()
        return cls.from_dict(data_dict)

    @classmethod
    def from_dict(cls, data: dict, orient='columns', dtype=None, columns=None):
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

                if _field > -100:   # type: ignore
                    valid_field_num += 1

                res += f"{_field:13.5f}{_field_qc:7d}"
            res += "\n"

        # add ending record
        for (key, qc_key) in zip(fields, qc_fields):
            res += f"{-777777:13.5f}{0:7d}"
        res += "\n"

        # add tail integers
        res += f"{valid_field_num:7d}{0:7d}{0:7d}"

        return res


class LittleR(LittleRData):
    
    _metadata = ["little_r_head"]
    
    def __init__(
        self,
        data=None,
        index=None,
        columns=None,
        data_header: Union[dict, None] = None,
        pressure: Union[np.ndarray, float] = 100000.,
        height: Union[np.ndarray, float] = -888888.,
        temperature: Union[np.ndarray, float] = 264.,
        dew_point: Union[np.ndarray, float] = 263.,
        wind_speed: Union[np.ndarray, float] = -888888.,
        wind_direction: Union[np.ndarray, float] = -888888.,
        wind_u: Union[np.ndarray, float] = -888888.,
        wind_v: Union[np.ndarray, float] = -888888.,
        relative_humidity: Union[np.ndarray, float] = -888888.,
        thickness: Union[np.ndarray, float] = -888888.,
        qulity_control_flag: Union[np.ndarray, dict, int] = 0,
        **kwargs
    ) -> None:
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
            qulity_control_flag=qulity_control_flag,
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
        """Head info of little_r obs data.

        :param longitude: Longitude.
        :type longitude: float
        :param latitude: Latitude.
        :type latitude: float
        :param fm: Platform code (FM-Code).
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
    def from_csv(cls, csv_path):
        return super().from_csv(csv_path)
    
    def to_zlr(self, file_path: str):
        if not file_path.endswith(".zlr"):
            file_path = f"{file_path}.zlr"

        with ZipFile(file_path, "w") as zip_file:
            with zip_file.open("header", "w") as header_file:
                header_file.write(dumps(self.little_r_head).encode())

            with zip_file.open("data", "w") as data_file:
                self.to_csv(data_file, index=False)

    @classmethod
    def from_zlr(cls, file_path: str):
        with ZipFile(file_path, "r") as zip_file:
            with zip_file.open("header", "r") as header_file:
                header = loads(header_file.read().decode())
            
            with zip_file.open("data", "r") as data_file:
                little_r = cls.from_csv(data_file)

        little_r.set_header(**header)   # type: ignore

        return little_r


__all__ = ["LittleRHead", "LittleRData", "LittleR"]
