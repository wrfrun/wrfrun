"""
wrfrun.model.arps.exec_wrap
###########################

Function wrapper of ARPS :doc:`Executables </api/model.arps.core>`.

.. autosummary::
    :toctree: generated/

    arpssfc
    arps
    arps3dvar
    ext2arps
"""

from typing import Optional

from wrfrun.core import WRFRUN

from .core import ARPS, ARPSSFC, EXT2ARPS, ARPS3DVar


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
    EXT2ARPS(arpstrn_data_path=arpstrn_data_path)()


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
    ARPS(
        arpssfc_data_path=arpssfc_data_path,
        ext2arps_data_path=ext2arps_data_path,
        core_num=WRFRUN.config.get_core_num(),
    )()


def arps3dvar(arps_data_path: Optional[str] = None):
    """
    Function interface for :class:`ARPS3DVar <wrfrun.model.arps.core.ARPS3DVar>`.

    :param arps_data_path: Directory containing ``arps.hdf000000`` and
                           ``arps.hdfgrdbas``. If it is ``None``, use the
                           archived ARPS output directory.
    :type arps_data_path: str | None
    """
    ARPS3DVar(arps_data_path=arps_data_path)()


__all__ = ["arpssfc", "arps", "arps3dvar", "ext2arps"]
