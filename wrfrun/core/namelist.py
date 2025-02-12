from copy import deepcopy
from os.path import exists
from typing import Union, Tuple

import f90nml

from wrfrun.utils import logger


CUSTOM_NAMELIST_TYPE = ("param", "goos", "geog_static_data")


class _Namelist:
    def __init__(self):
        self._wps_namelist = {}
        self._wrf_namelist = {}
        self._wrfda_namelist = {}
        self._custom_namelist = {}

    def read_namelist(self, file_path: str, namelist_type: str):
        """
        Read namelist.

        Args:
            file_path: File path.
            namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.

        Returns:

        """
        # check the file path
        if not exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError

        if namelist_type == "wps":
            self._wps_namelist = f90nml.read(file_path).todict()
        elif namelist_type == "wrf":
            self._wrf_namelist = f90nml.read(file_path).todict()
        elif namelist_type == "wrfda":
            self._wrfda_namelist = f90nml.read(file_path).todict()
        else:
            global CUSTOM_NAMELIST_TYPE
            if namelist_type not in CUSTOM_NAMELIST_TYPE:
                logger.error(f"Unknown namelist type: {namelist_type}, register it first.")
                raise ValueError(f"Unknown namelist type: {namelist_type}, register it first.")
            else:
                self._custom_namelist[namelist_type] = f90nml.read(file_path).todict()

    def write_namelist(self, save_path: str, namelist_type: str, overwrite=True):
        """
        Write namelist to file.

        Args:
            save_path: File path.
            namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.
            overwrite: If overwrite existed file, defaults to ``True``.

        Returns:

        """
        if namelist_type == "wps":
            f90nml.Namelist(self._wps_namelist).write(save_path, force=overwrite)
        elif namelist_type == "wrf":
            f90nml.Namelist(self._wrf_namelist).write(save_path, force=overwrite)
        elif namelist_type == "wrfda":
            f90nml.Namelist(self._wrfda_namelist).write(save_path, force=overwrite)
        else:
            global CUSTOM_NAMELIST_TYPE
            if namelist_type not in CUSTOM_NAMELIST_TYPE:
                logger.error(f"Unknown namelist type: {namelist_type}")
                raise ValueError(f"Unknown namelist type: {namelist_type}")

            if namelist_type not in self._custom_namelist:
                logger.error(f"Can't found custom namelist '{namelist_type}', maybe you forget to read it first")
                raise KeyError(f"Can't found custom namelist '{namelist_type}', maybe you forget to read it first")

            f90nml.Namelist(self._custom_namelist[namelist_type]).write(save_path, force=overwrite)
        
    def update_namelist(self, new_values: Union[str, dict], namelist_type: str):
        """
        Update value in namelist data.

        You can give your custom namelist file, a whole namelist or a file only contains values you want to change.

        >>> from wrfrun.core import WRFRUNNamelist
        >>> namelist_file = "./namelist.wps"
        >>> WRFRUNNamelist.update_namelist(namelist_file, namelist_type="wps")
        
        >>> from wrfrun.core import WRFRUNNamelist
        >>> namelist_file = "./namelist.wrf"
        >>> WRFRUNNamelist.update_namelist(namelist_file, namelist_type="wrf")

        Or give a Dict object contains values you want to change.
        
        >>> from wrfrun.core import WRFRUNNamelist
        >>> namelist_values = {"ungrib": {"prefix": "./output/FILE"}}
        >>> WRFRUNNamelist.update_namelist(namelist_values, namelist_type="wps")

        >>> from wrfrun.core import WRFRUNNamelist
        >>> namelist_values = {"time_control": {"debug_level": 100}}
        >>> WRFRUNNamelist.update_namelist(namelist_values, namelist_type="wrf")

        Args:
            new_values: New values.
            namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.

        Returns:

        """
        if namelist_type == "wps":
            reference = self._wps_namelist
        elif namelist_type == "wrf":
            reference = self._wrf_namelist
        elif namelist_type == "wrfda":
            reference = self._wrfda_namelist
        else:
            global CUSTOM_NAMELIST_TYPE
            if namelist_type not in CUSTOM_NAMELIST_TYPE:
                logger.error(f"Unknown namelist type: {namelist_type}")
                raise ValueError(f"Unknown namelist type: {namelist_type}")
            elif namelist_type not in self._custom_namelist:
                self._custom_namelist[namelist_type] = new_values
                return
            else:
                reference = self._custom_namelist[namelist_type]

        if isinstance(new_values, str):
            if not exists(new_values):
                logger.error(f"File not found: {new_values}")
                raise FileNotFoundError
            new_values = f90nml.read(new_values).todict()

        for key in new_values:
            if key in reference:
                reference[key].update(new_values[key])
            else:
                reference[key] = new_values[key]

    def get_namelist(self, namelist_type: str) -> dict:
        """
        Get specific namelist.

        Args:
            namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.

        Returns:

        """
        if namelist_type == "wps":
            return deepcopy(self._wps_namelist)
        elif namelist_type == "wrf":
            return deepcopy(self._wrf_namelist)
        elif namelist_type == "wrfda":
            return deepcopy(self._wrfda_namelist)
        else:
            global CUSTOM_NAMELIST_TYPE
            if namelist_type not in CUSTOM_NAMELIST_TYPE:
                logger.error(f"Unknown namelist type: {namelist_type}")
                raise ValueError(f"Unknown namelist type: {namelist_type}")
            elif namelist_type not in self._custom_namelist:
                return {}
            else:
                return deepcopy(self._custom_namelist[namelist_type])

    def delete_namelist(self, namelist_type: str):
        """
        Delete specified namelist values.

        :param namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.
        :type namelist_type: str
        :return:
        :rtype:
        """
        if namelist_type == "wps":
            self._wps_namelist = {}
        elif namelist_type == "wrf":
            self._wrf_namelist = {}
        elif namelist_type == "wrfda":
            self._wrfda_namelist = {}
        else:
            global CUSTOM_NAMELIST_TYPE
            if namelist_type not in CUSTOM_NAMELIST_TYPE:
                logger.error(f"Unknown namelist type: {namelist_type}")
                raise ValueError(f"Unknown namelist type: {namelist_type}")

            if namelist_type not in self._custom_namelist:
                return

            self._custom_namelist.pop(namelist_type)


WRFRUNNamelist = _Namelist()


def register_custom_namelist_type(namelist_type: str) -> bool:
    """
    Register any namelist type so you can read, update and write it later via ``WRFRUNNamelist``.

    :param namelist_type: A unique namelist type.
    :type namelist_type: str
    :return: True if register successfully, else False.
    :rtype: bool
    """
    global CUSTOM_NAMELIST_TYPE
    if namelist_type in CUSTOM_NAMELIST_TYPE:
        return False

    else:
        CUSTOM_NAMELIST_TYPE = CUSTOM_NAMELIST_TYPE + (namelist_type, )
        return True


def unregister_custom_namelist_type(namelist_type: str):
    """
    Unregister specified namelist type.
    If unregister successfully, all data about this namelist kind will be lost.

    :param namelist_type: A unique namelist type.
    :type namelist_type: str
    :return:
    :rtype:
    """
    global CUSTOM_NAMELIST_TYPE, WRFRUNNamelist
    if namelist_type not in CUSTOM_NAMELIST_TYPE:
        return

    WRFRUNNamelist.delete_namelist(namelist_type)

    CUSTOM_NAMELIST_TYPE = tuple(set(CUSTOM_NAMELIST_TYPE) - {namelist_type, })


def read_namelist(file_path: str, namelist_type: str):
    """
    Read namelist.

    Args:
        file_path: File path.
        namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.

    Returns:

    """
    global WRFRUNNamelist
    WRFRUNNamelist.read_namelist(file_path, namelist_type)


def write_namelist(save_path: str, namelist_type: str, overwrite=True):
    """
    Write namelist to file.

    Args:
        save_path: File path.
        namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.
        overwrite: If overwrite existed file, defaults to ``True``.

    Returns:

    """
    global WRFRUNNamelist
    WRFRUNNamelist.write_namelist(save_path, namelist_type, overwrite=overwrite)


def update_namelist(new_values: Union[str, dict], namelist_type: str):
    """
    Update value in namelist data.
    
    Args:
        new_values: New values.
        namelist_type: ``"wps"``, ``"wrf"``, ``"wrfda"``, or any other type in ``CUSTOM_NAMELIST_TYPE``.

    Returns:

    """
    global WRFRUNNamelist
    WRFRUNNamelist.update_namelist(new_values, namelist_type)


def get_start_end_date_and_interval_hours() -> Tuple[str, str, int]:
    """Get start date, end date and interval hours from namelist

    Returns:
        Tuple[str, str, int]: start date, end date, interval hours
    """
    global WRFRUNNamelist
    # get start_date, end_date and interval_seconds
    start_date = WRFRUNNamelist.get_namelist("wps")["share"]["start_date"][0]
    end_date = WRFRUNNamelist.get_namelist("wps")["share"]["end_date"][0]
    interval_hours = WRFRUNNamelist.get_namelist("wps")["share"]["interval_seconds"] // 3600

    # change format
    start_date = start_date.split('_')
    start_date = f"{start_date[0]} {start_date[1]}"
    end_date = end_date.split('_')
    end_date = f"{end_date[0]} {end_date[1]}"

    return start_date, end_date, interval_hours


__all__ = ["read_namelist", "write_namelist", "update_namelist", "WRFRUNNamelist", "get_start_end_date_and_interval_hours", "register_custom_namelist_type",
           "unregister_custom_namelist_type"]
