"""
wrfrun.model.wrf.geodata
########################

Functions to read and write WPS geographical static data.

.. autosummary::
    :toctree: generated/

    _get_data_type
    _get_clip_area
    parse_geographical_data_index
    parse_geographical_data_file
    read_geographical_static_data
"""

from os import listdir
from os.path import exists
from typing import OrderedDict, Union

import numpy as np
from xarray import DataArray

from wrfrun.core import WRFRUN
from wrfrun.log import logger

# for example: 00001-00200.00201-00400
DATA_NAME_TEMPLATE = "{}-{}.{}-{}"


def _get_data_type(wordsize: int) -> type:
    """
    Get data type based on wordsize value in index file.

    :param wordsize: Wordsize in index file.
    :type wordsize: int
    :return: NumPy value type.
    :rtype: type
    """
    # define map dict
    map_dict = {1: np.int8, 2: np.int16, 4: np.int32}

    return map_dict[wordsize]


def _get_clip_area(
    index_area: tuple[int, int, int, int], row_num: int, col_num: int, tile_x: int, tile_y: int
) -> tuple[int, int, int, int]:
    """
    Get clip area.

    :param index_area: Full area index.
    :type index_area: tuple[int, int, int, int]
    :param row_num: Row number of the tile.
    :type row_num: int
    :param col_num: Column number of the file.
    :type col_num: int
    :param tile_x: X size of the tile.
    :type tile_x: int
    :param tile_y: Y size of the tile.
    :type tile_y: int
    :return: Clip area.
    :rtype: tuple[int, int, int, int]
    """
    # calculate tile area
    tile_area = (
        col_num * tile_x + 1,
        col_num * tile_x + tile_x,
        row_num * tile_y + 1,
        row_num * tile_y + tile_y,
    )

    # generate clip area
    clip_area = (
        0 if index_area[0] <= tile_area[0] else index_area[0] % tile_x - 1,
        tile_x if index_area[1] >= tile_area[1] else index_area[1] % tile_x - 1,
        0 if index_area[2] <= tile_area[2] else index_area[2] % tile_y - 1,
        tile_y if index_area[3] >= tile_area[3] else index_area[3] % tile_y - 1,
    )

    return clip_area


def parse_geographical_data_index(index_path: str) -> OrderedDict:
    """
    Read geographical data index file.

    :param index_path: Index file path.
    :type index_path: str
    :return: Info stored in dict.
    :rtype: OrderedDict[Any, Any]
    """
    # since the index file is very similar to fortran namelist file,
    # we can manually add "&index" and "/" and parse it as a namelist
    # temp file store path
    WRFRUNConfig = WRFRUN.config
    temp_file = f"{WRFRUNConfig.WRFRUN_TEMP_PATH}/geogrid_data.index"
    temp_file = WRFRUNConfig.parse_resource_uri(temp_file)

    # open file and add header and tail
    with open(index_path, "r") as _index_file:
        with open(temp_file, "w") as _temp_file:
            _temp_file.write("&index\n")
            _temp_file.write(_index_file.read())
            _temp_file.write("/")

    # read index
    WRFRUNConfig.read_namelist(temp_file, "geog_static_data")

    return WRFRUNConfig.get_namelist("geog_static_data")["index"]


def parse_geographical_data_file(
    file_path: str,
    wordsize: int,
    endian: str,
    tile_shape: tuple[int, ...],
    area: Union[tuple[int, ...], None] = None,
    miss_value: Union[int, float, None] = None,
) -> np.ndarray:
    """
    Read geographical data file.

    :param file_path: File path.
    :type file_path: str
    :param wordsize: How many bytes are used to store value in data file.
    :type wordsize: int
    :param endian: "big" or "little".
    :type endian: str
    :param tile_shape: The raw shape of the tile. Can be 2D or 3D.
    :type tile_shape: tuple[int, ...]
    :param area: The range (x_start, x_stop, y_start, y_stop, ...) of data you want to read. Defaults to None.
    :type area: Union[tuple[int, ...], None]
    :param miss_value: The value which represents NaN. Defaults to None.
    :type miss_value: Union[int, float, None]
    :return: NumPy array object.
    :rtype: ndarray[Any, Any]
    """
    # get data type
    data_type = _get_data_type(wordsize)

    # read data
    data = np.fromfile(file_path, dtype=data_type)

    # swap byte if it needs
    if endian == "big":
        data = data.byteswap()

    # reshape
    data = data.reshape(tile_shape)

    # clip
    if area:
        # check area
        if len(area) % 2 != 0:
            logger.error(f"The length of `area` must be even, but is {len(area)}")
            exit(1)

        area_array = np.asarray(area).reshape(-1, 2)
        slice_index = tuple((slice(i[0], i[1]) for i in area_array))

        if len(slice_index) == 2:
            slice_index += (slice(None),)

        data = data[slice_index[::-1]]  # type: ignore

    # fill nan
    if miss_value:
        data[data == miss_value] = np.nan

    return data


def read_geographical_static_data(
    geog_data_folder_path: str, name: str, area: Union[tuple[float, float, float, float], None] = None
) -> DataArray:
    """
    Read WPS geographical static data

    :param geog_data_folder_path: Data folder path.
    :type geog_data_folder_path: str
    :param name: Name that will be used to create DataArray.
    :type name: str
    :param area: Longitude and latitude area (lon_start, lon_stop, lat_start, lat_stop). Defaults to None.
    :type area: Union[tuple[float, float, float, float], None]
    :return: DataArray object.
    :rtype: DataArray
    """
    # check if folder exists
    if not exists(geog_data_folder_path):
        logger.error(f"Can't find folder {geog_data_folder_path}")
        exit(1)

    # parse index file first
    index_path = f"{geog_data_folder_path}/index"
    index_data = parse_geographical_data_index(index_path)

    # extract info to read data
    # # check essential key
    if "wordsize" not in index_data:
        logger.error("Can't find key `wordsize` in index file, maybe it is corrupted.")
        exit(1)
    # # extract info
    wordsize = index_data["wordsize"]
    endian = "little" if "endian" not in index_data else index_data["endian"]
    miss_value = None if "missing_value" not in index_data else index_data["missing_value"]
    tile_shape = []
    for key in ["tile_z", "tile_y", "tile_x"]:
        if key in index_data:
            tile_shape.append(index_data[key])
    tile_shape = tuple(tile_shape)
    known_lat = index_data["known_lat"]
    known_lon = index_data["known_lon"]
    dx = index_data["dx"]
    dy = index_data["dy"]

    # calculate area
    if area:
        # read resolution, latitude and longitude
        index_area = (
            int((area[0] - known_lon) // dx),
            int((area[1] - known_lon) // dx),
            int((area[2] - known_lat) // dy),
            int((area[3] - known_lat) // dy),
        )
        # check if negative value exists
        if index_area[0] < 0 or index_area[2] < 0:
            logger.warning("Part of your area has exceeded data's area")
            # set negative value to 0
            index_area = tuple((i if i >= 0 else 0 for i in index_area))
    else:
        logger.warning("You want to read all data, which may be very large")
        index_area = None

    # find the file we need to read
    if index_area:
        # # calculate tile index number
        tile_index_num = (
            index_area[0] // tile_shape[-1],
            index_area[1] // tile_shape[-1],
            index_area[2] // tile_shape[-2],
            index_area[3] // tile_shape[-2],
        )

        filenames = []
        # # generate filenames and clip area
        for row_num in range(tile_index_num[2], tile_index_num[3] + 1):
            _names = []
            for col_num in range(tile_index_num[0], tile_index_num[1] + 1):
                _names.append(
                    [
                        DATA_NAME_TEMPLATE.format(
                            str(col_num * tile_shape[-1] + 1).rjust(5, "0"),
                            str((col_num + 1) * tile_shape[-1]).rjust(5, "0"),
                            str(row_num * tile_shape[-2] + 1).rjust(5, "0"),
                            str((row_num + 1) * tile_shape[-2]).rjust(5, "0"),
                        ),
                        _get_clip_area(index_area, row_num, col_num, tile_shape[-1], tile_shape[-2]),  # type: ignore
                    ]
                )

            filenames.append(_names)
    else:
        raw_filenames = [x for x in listdir(geog_data_folder_path) if x != "index"]
        raw_filenames.sort()

        # parse the last file to get row number and column number
        _last_filename = raw_filenames[-1]
        total_col_num = int(_last_filename.split(".")[0].split("-")[1]) // tile_shape[-1]
        total_row_num = int(_last_filename.split(".")[1].split("-")[1]) // tile_shape[-2]

        filenames = []

        for row_num in range(total_row_num):
            _names = []
            for col_num in range(total_col_num):
                _names.append([raw_filenames[row_num * total_col_num + col_num], None])

            filenames.append(_names)

    # read and concatenate
    array = []
    for _row in filenames:
        _array = []
        for _col in _row:
            _array.append(
                parse_geographical_data_file(
                    f"{geog_data_folder_path}/{_col[0]}", wordsize, endian, tile_shape, _col[1], miss_value
                )
            )

        # concatenate _array
        array.append(np.concatenate(_array, axis=-1))

    array = np.concatenate(array, axis=-2)

    # get the longitude and latitude of the start point
    if index_area:
        longitude = known_lon + dx * index_area[0]
        latitude = known_lat + dy * index_area[2]
    else:
        longitude = known_lon
        latitude = known_lat

    longitude = np.arange(array.shape[-1]) * dx + longitude
    latitude = np.arange(array.shape[-2]) * dy + latitude
    levels = np.arange(array.shape[-3])

    return DataArray(
        name=name,
        data=array,
        dims=["levels", "latitude", "longitude"],
        coords={"longitude": longitude, "latitude": latitude, "levels": levels},
        attrs=index_data,
    )


__all__ = ["parse_geographical_data_index", "parse_geographical_data_file", "read_geographical_static_data"]
