"""
wrfrun.model.arps.exec_wrap
###########################

Function wrapper of ARPS :doc:`Executables </api/model.arps.core>`.

.. autosummary::
    :toctree: generated/

    arpssfc
    arps
    ext2arps
"""

from wrfrun.core import WRFRUN

from .core import ARPS, ARPSSFC, EXT2ARPS


def arpssfc():
    """
    Function interface for :class:`ARPSSFC <wrfrun.model.arps.core.ARPSSFC>`.
    """
    ARPSSFC()()


def ext2arps():
    """
    Function interface for :class:`EXT2ARPS <wrfrun.model.arps.core.EXT2ARPS>`.
    """
    EXT2ARPS()()


def arps():
    """
    Function interface for :class:`ARPS <wrfrun.model.arps.core.ARPS>`.
    """
    ARPS(WRFRUN.config.get_core_num())()


__all__ = ["arpssfc", "arps", "ext2arps"]
