"""
wrfrun.model.constants
######################

Definition of constants used by models.

.. autosummary::
    :toctree: generated/

    NamelistName
"""

from dataclasses import dataclass


@dataclass
class NamelistName:
    """
    Namelist file names.

    .. py:attribute:: WPS
        :type: str
        :value: namelist.wps

        WPS namelist file name.

    .. py:attribute:: WRF
        :type: str
        :value: namelist.input

        WRF namelist file name.

    .. py:attribute:: WRFDA
        :type: str
        :value: namelist.input

        WRFDA namelist file name.
    """

    WPS = "namelist.wps"
    WRF = "namelist.input"
    WRFDA = "namelist.input"


__all__ = ["NamelistName"]
