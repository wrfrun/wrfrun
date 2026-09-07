"""
wrfrun.model.arps.exec_wrap
###########################

Function wrapper of ARPS :doc:`Executables </api/model.arps.core>`.

.. autosummary::
    :toctree: generated/

    arpssfc
    arps
    arps3dvar
    arpsintrp
    ext2arps
"""

from typing import Optional

from wrfrun.core import WRFRUN_NEW

from .core import ARPS, ARPSSFC, EXT2ARPS, ARPS3DVar, ARPSIntrp


def arpssfc():
    """
    Function interface for :class:`ARPSSFC <wrfrun.model.arps.core.ARPSSFC>`.
    """
    ARPSSFC()()


def ext2arps(arpstrn_data_path: Optional[str] = None):
    """
    Function interface for :class:`EXT2ARPS <wrfrun.model.arps.core.EXT2ARPS>`.

    :param arpstrn_data_path: Directory path of :class:`ARPSTRN <wrfrun.model.arps.arpstrn.ARPSTRN>` outputs.
                              If is ``None``, try to use the output path specified by config file.
    :type arpstrn_data_path: str
    """
    EXT2ARPS()()


def arps(arpssfc_data_path: Optional[str] = None, ext2arps_data_path: Optional[str] = None):
    """
    Function interface for :class:`ARPS <wrfrun.model.arps.core.ARPS>`.

    :param arpssfc_data_path: Directory path of :class:`ARPSSFC` outputs.
                              If is ``None``, try to use the output path specified by config file.
    :type arpssfc_data_path: str
    :param ext2arps_data_path: Directory path of :class:`EXT2ARPS` outputs.
                              If is ``None``, try to use the output path specified by config file.
    :type ext2arps_data_path: str
    """
    ARPS(core_num=WRFRUN_NEW.config.get_core_num())()


def arps3dvar(arps_data_path: Optional[str] = None):
    """
    Function interface for :class:`ARPS3DVar <wrfrun.model.arps.core.ARPS3DVar>`.

    :param arps_data_path: Directory containing ``arps.hdf000000`` and
                           ``arps.hdfgrdbas``. If it is ``None``, use the
                           archived ARPS output directory.
    :type arps_data_path: str | None
    """
    ARPS3DVar()()


def arpsintrp():
    """
    Function interface for :class:`ARPSIntrp <wrfrun.model.arps.core.ARPSIntrp>`.
    """
    ARPSIntrp()()


__all__ = ["arpssfc", "arps", "arps3dvar", "arpsintrp", "ext2arps"]
