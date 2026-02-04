"""
wrfrun.core._namelist
#####################

.. autosummary::
    :toctree: generated/

    NamelistMixIn

NamelistMixIn
*************

This class provides methods to manage namelist settings of NWP models.
It can read namelist files, change namelist values or write values to a namelist file.

Namelist values are stored with a unique ``namelist_id``,
which enables wrfrun to manage multiple namelist settings simultaneously.

**Read namelist file**

.. code-block:: Python
    :caption: main.py

    namelist = NamelistMixIn()
    namelist_file_path = "./namelist.wps"
    namelist_id = "wps"

    # remember to check namelist id first
    if not namelist.check_namelist_id(namelist_id):
        namelist.register_namelist_id(namelist_id)

    # read namelist file
    namelist.read_namelist(namelist_file_path, namelist_id)

**Write namelist file**

.. code-block:: Python
    :caption: main.py

    namelist_file_path = "./namelist.wps"
    namelist_id = "wps"

    # will overwrite existing file by default.
    namelist.write_namelist(namelist_file_path, namelist_id)
    # doesn't overwrite existing file
    namelist.write_namelist(namelist_file_path, namelist_id, overwrite=False)

**Update namelist values**

1. You can provide a whole namelist file

.. code-block:: Python
    :caption: main.py

    namelist_file_path = "./namelist.wps"
    namelist_id = "wps"

    namelist.update_namelist(namelist_file_path, namelist_id)

2. Or just some values in a dictionary

.. code-block:: Python
    :caption: main.py

    namelist_value = {"share": {"max_dom": 1}}
    namelist_id = "wps"

    namelist.update_namelist(namelist_value, namelist_id)
"""

from copy import deepcopy
from os.path import exists
from typing import Union

import f90nml

from ..log import logger
from .error import NamelistError, NamelistIDError


class NamelistMixIn:
    """
    Manage namelist settings of NWP models.
    """

    def __init__(self, *args, **kwargs):
        self._namelist_dict = {}
        self._namelist_id_list: tuple[str, ...] = ("param", "geog_static_data", "wps", "wrf", "wrfda", "palm")

        super().__init__(*args, **kwargs)

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

    def read_namelist(self, file_path: str, namelist_id: str):
        """
        Read namelist values from a file and store them with the ``namelist_id``.

        If ``wrfrun`` can't read the file, :class:`FileNotFoundError` will be raised.
        If ``namelist_id`` isn't registered, :class:`NamelistIDError <wrfrun.core.error.NamelistIDError>` will be raised.

        :param file_path: Namelist file path.
        :type file_path: str
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        # check the file path
        if not exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError

        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

        self._namelist_dict[namelist_id] = f90nml.read(file_path).todict()

    def write_namelist(self, save_path: str, namelist_id: str, overwrite=True):
        """
        Write namelist values of a ``namelist_id`` to a file.

        If ``namelist_id`` hasn't been registered, or its namelist value can't be found,
        :class:`NamelistIDError <wrfrun.core.error.NamelistIDError>` will be raised.

        :param save_path: Target file path.
        :type save_path: str
        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :param overwrite: If overwrite the existed file.
        :type overwrite: bool
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

        if namelist_id not in self._namelist_dict:
            logger.error(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
            raise NamelistError(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")

        f90nml.Namelist(self._namelist_dict[namelist_id]).write(save_path, force=overwrite)

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
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")

        elif namelist_id not in self._namelist_dict:
            self._namelist_dict[namelist_id] = new_values
            return

        else:
            reference = self._namelist_dict[namelist_id]

        if isinstance(new_values, str):
            if not exists(new_values):
                logger.error(f"File not found: {new_values}")
                raise FileNotFoundError(f"File not found: {new_values}")
            new_values = f90nml.read(new_values).todict()

        for key in new_values:
            if key in reference:
                reference[key].update(new_values[key])
            else:
                reference[key] = new_values[key]

    def get_namelist(self, namelist_id: str) -> dict:
        """
        Get namelist values of a ``namelist_id``.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        :return: A dictionary which contains namelist values.
        :rtype: dict
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
            raise NamelistIDError(f"Unknown namelist id: {namelist_id}, register it first.")
        elif namelist_id not in self._namelist_dict:
            logger.error(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
            raise NamelistError(f"Can't found custom namelist '{namelist_id}', maybe you forget to read it first")
        else:
            return deepcopy(self._namelist_dict[namelist_id])

    def delete_namelist(self, namelist_id: str):
        """
        Delete namelist values of a ``namelist_id``.

        :param namelist_id: Registered ``namelist_id``.
        :type namelist_id: str
        """
        if namelist_id not in self._namelist_id_list:
            logger.error(f"Unknown namelist id: {namelist_id}, register it first.")
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


__all__ = ["NamelistMixIn"]
