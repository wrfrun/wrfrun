"""
wrfrun.core.session._namelist
#############################

Manager namelist used by the session.

.. autosummary::
    :toctree: generated/

    NamelistMixIn

NamelistMixIn
*************

This mixin provides methods to manage namelist used by the session.

Namelist values are stored with a unique ``namelist_id``,
which enables wrfrun to manage multiple namelist settings simultaneously.

TODO: Check examples here.

**Read namelist file**

.. code-block:: Python
    :caption: main.py

    from wrfrun.core import WRFRUN
    from wrfrun.run import WRFRun

    with WRFRun("/path/to/config.toml") as wrf_run:
        _session = WRFRUN.session

        namelist_file_path = "./namelist.wps"
        namelist_id = "wps"

        # remember to check namelist id first
        if not _session.namelist.check_namelist_id(namelist_id):
            _session.namelist.register_namelist_id(namelist_id)

        # read namelist file
        _session.namelist.read_namelist(namelist_file_path, namelist_id)

**Write namelist file**

.. code-block:: Python
    :caption: main.py

    from wrfrun.core import WRFRUN
    from wrfrun.run import WRFRun

    with WRFRun("/path/to/config.toml") as wrf_run:
        _session = WRFRUN.session

        namelist_file_path = "./namelist.wps"
        namelist_id = "wps"

        # will overwrite existing file by default.
        _session.namelist.write_namelist(namelist_file_path, namelist_id)
        # doesn't overwrite existing file
        _session.namelist.write_namelist(namelist_file_path, namelist_id, overwrite=False)

**Update namelist values**

1. You can provide a whole namelist file

.. code-block:: Python
    :caption: main.py

    from wrfrun.core import WRFRUN
    from wrfrun.run import WRFRun

    with WRFRun("/path/to/config.toml") as wrf_run:
        _session = WRFRUN.session

        namelist_file_path = "./namelist.wps"
        namelist_id = "wps"

        _session.namelist.update_namelist(namelist_file_path, namelist_id)

2. Or just some values in a dictionary

.. code-block:: Python
    :caption: main.py

    from wrfrun.core import WRFRUN
    from wrfrun.run import WRFRun

    with WRFRun("/path/to/config.toml") as wrf_run:
        _session = WRFRUN.session

        namelist_value = {"share": {"max_dom": 1}}
        namelist_id = "wps"

        _session.namelist.update_namelist(namelist_value, namelist_id)
"""

import logging
from copy import deepcopy
from os.path import exists
from typing import Union

import f90nml

from ..error import NamelistError, NamelistIDError
from ..runtime.io import IOService
from ..type import ResourceRef

LOGGER = logging.getLogger("wrfrun")


class NamelistService:
    """
    Manage namelist settings.

    This MixIn targets to store read only namelist settings.
    If you want to save namelist to a file, get it and save it by yourself.
    """

    def __init__(self, io: IOService):
        """
        Namelist stores.

        :param io: IO service.
        :type io: IOService
        """
        self._namelist_dict = {}
        self._namelist_id_list: tuple[str, ...] = (
            "param",
            "geog_static_data",
            "wps",
            "wrf",
            "wrfda",
            "palm",
            "arps",
        )

        self._io = io

    def register_namelist_id(self, namelist_id: str) -> bool:
        """
        Register a unique ``namelist_id`` so you can read, update and write namelist with it later.

        :param namelist_id: A unique namelist id.
        :type namelist_id: str
        :return: True if register successfully, else False.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list:
            return False

        else:
            self._namelist_id_list += (namelist_id,)
            return True

    def unregister_namelist_id(self, namelist_id: str):
        """
        Unregister a ``namelist_id``.
        If unregister successfully, all values of this namelist will be deleted.

        :param namelist_id: A unique namelist id.
        :type namelist_id: str
        """
        if namelist_id not in self._namelist_id_list:
            return

        self.delete_namelist(namelist_id)
        self._namelist_id_list = tuple(
            set(self._namelist_id_list)
            - {
                namelist_id,
            }
        )

    def check_namelist_id(self, namelist_id: str) -> bool:
        """
        Check if a ``namelist_id`` is registered.

        :param namelist_id: A ``namelist_id``.
        :type namelist_id: str
        :return: True if the ``namelist_id`` is registered, else False.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list:
            return True
        else:
            return False

    def read_namelist(self, new_values: Union[str, dict], namelist_id: str):
        """
        Read namelist values from a file or a dictionary, and store them with the ``namelist_id``.

        If ``wrfrun`` can't read the file, :class:`FileNotFoundError` will be raised.
        If ``namelist_id`` isn't registered, :class:`NamelistIDError <wrfrun.core.error.NamelistIDError>` will be raised.

        :param new_values: Namelist file path, or a Python dictionary.
        :type new_values: Union[str, dict]
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        if isinstance(new_values, str):
            # check the file path
            if not exists(new_values):
                LOGGER.error(f"File not found: {new_values}")
                raise FileNotFoundError

            if namelist_id not in self._namelist_id_list:
                LOGGER.error(f"Unknown namelist id: {namelist_id}, register it first.")
                raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

            self._namelist_dict[namelist_id] = f90nml.read(new_values).todict()

        elif isinstance(new_values, dict):
            self._namelist_dict[namelist_id] = deepcopy(new_values)

        else:
            LOGGER.error(f"Unknow type of 'new_values': {type(new_values)}")
            raise TypeError(f"Unknow type of 'new_values': {type(new_values)}")

    def update_namelist(self, new_values: Union[str, dict], namelist_id: str):
        """
        Update namelist values of a ``namelist_id``.

        You can give the path of a whole namelist file or a file only contains values you want to change.

        >>> from wrfrun.core import WRFRUN
        >>> namelist_file = "./namelist.wps"
        >>> WRFRUN.config.update_namelist(namelist_file, namelist_id="wps")

        >>> namelist_file = "./namelist.wrf"
        >>> WRFRUN.config.update_namelist(namelist_file, namelist_id="wrf")

        You can also give a dictionary contains values you want to change.

        >>> namelist_values = {"ungrib": {"prefix": "./output/FILE"}}
        >>> WRFRUN.config.update_namelist(namelist_values, namelist_id="wps")

        >>> namelist_values = {"time_control": {"debug_level": 100}}
        >>> WRFRUN.config.update_namelist(namelist_values, namelist_id="wrf")

        :param new_values: The path of a namelist file, or a dict contains namelist values.
        :type new_values: str | dict
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        if isinstance(new_values, str):
            if not exists(new_values):
                LOGGER.error(f"File not found: {new_values}")
                raise FileNotFoundError(f"File not found: {new_values}")
            new_values = f90nml.read(new_values).todict()

        if namelist_id not in self._namelist_id_list:
            LOGGER.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

        elif namelist_id not in self._namelist_dict:
            self._namelist_dict[namelist_id] = new_values
            return

        else:
            reference = self._namelist_dict[namelist_id]

        for key in new_values:
            if key in reference:
                if isinstance(reference[key], dict):
                    reference[key].update(new_values[key])

                else:
                    reference[key] = new_values[key]

            else:
                reference[key] = new_values[key]

        self._namelist_dict[namelist_id] = reference

    def get_namelist(self, namelist_id: str) -> dict:
        """
        Get namelist values of a ``namelist_id``.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :return: A dictionary which contains namelist values.
        :rtype: dict
        """
        if namelist_id not in self._namelist_id_list:
            LOGGER.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")
        elif namelist_id not in self._namelist_dict:
            LOGGER.error(f"Can't found namelist '{namelist_id}', maybe you forget to read it first")
            raise NamelistError(f"Can't found namelist '{namelist_id}', maybe you forget to read it first")
        else:
            return deepcopy(self._namelist_dict[namelist_id])

    def write_namelist(self, save_path: str | ResourceRef, namelist_id: str):
        """
        Write namelist to a file.

        :param save_path: File path or resource ref.
        :type save_path: str | ResourceRef
        :param namelist_id: Namelist ID.
        :type namelist_id: str
        """
        self._io.write_namelist(
            self.get_namelist(namelist_id),
            save_path,
        )

    def delete_namelist(self, namelist_id: str):
        """
        Delete namelist values of a ``namelist_id``.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        if namelist_id not in self._namelist_id_list:
            LOGGER.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise ValueError(f"Unknown namelist id: {namelist_id}, register it first.")

        if namelist_id not in self._namelist_dict:
            return

        self._namelist_dict.pop(namelist_id)

    def check_namelist(self, namelist_id: str) -> bool:
        """
        Check if a namelist has been registered and loaded.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :return: ``True`` if it is registered and loaded, else ``False``.
        :rtype: bool
        """
        if namelist_id in self._namelist_id_list and namelist_id in self._namelist_dict:
            return True

        else:
            return False


__all__ = ["NamelistService"]
