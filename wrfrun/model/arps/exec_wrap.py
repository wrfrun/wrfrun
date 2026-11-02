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
    radremap
"""

from wrfrun.core import WRFRUN, ResultSource

from .core import ARPS, ARPSSFC, EXT2ARPS, ARPS3DVar, ARPSIntrp, ARPSTrn, RadRemap


def arpssfc():
    """
    Function interface for :class:`ARPSSFC <wrfrun.model.arps.core.ARPSSFC>`.
    """
    ARPSSFC()()


def ext2arps(arpstrn_source: ResultSource | None = None):
    """
    Function interface for :class:`EXT2ARPS <wrfrun.model.arps.core.EXT2ARPS>`.

    :param arpstrn_source: Source of ``arpstrn`` terrain outputs. If omitted,
                           use the latest published results.
    """
    EXT2ARPS(arpstrn_source)()


def arps(
    arpssfc_source: ResultSource | None = None,
    arpsintrp_source: ResultSource | None = None,
    history_source: ResultSource | None = None,
):
    """
    Function interface for :class:`ARPS <wrfrun.model.arps.core.ARPS>`.

    :param arpssfc_source: Source of ``arpssfc`` surface outputs. If omitted,
                           use the latest published results.
    :param arpsintrp_source: Source of ``arpsintrp`` boundary outputs. If
                             omitted, use the latest published results.
    :param history_source: Source of ARPS history and grid-base files. If
                           omitted, use ``data/inputs/.../arps``.
    """
    ARPS(
        core_num=WRFRUN.config.get_core_num(),
        arpssfc_source=arpssfc_source,
        arpsintrp_source=arpsintrp_source,
        history_source=history_source,
    )()


def arps3dvar(arps_source: ResultSource | None = None):
    """
    Function interface for :class:`ARPS3DVar <wrfrun.model.arps.core.ARPS3DVar>`.

    :param arps_source: Source of ARPS background files. If omitted, use the
                        latest published results.
    """
    ARPS3DVar(arps_source)()


def arpsintrp(history_source: ResultSource | None = None):
    """
    Function interface for :class:`ARPSIntrp <wrfrun.model.arps.core.ARPSIntrp>`.

    :param history_source: Source of ARPS history files. If omitted, use
                           ``data/inputs/.../arpsintrp``.
    """
    ARPSIntrp(
        history_source=history_source,
        core_num=WRFRUN.config.get_core_num(),
    )()


def radremap(arps_source: ResultSource | None = None):
    """
    Remap the radar volume configured in the project ``radremap`` namelist.

    The ARPS background is selected by ``initialization.inifile`` in
    ``configs/namelists/templates/arps/radremap/radremap.nml`` and optional
    project updates.

    :param arps_source: Source of ARPS background files. If omitted, use the
                        latest published results.

    .. code-block:: python

        from wrfrun.model.arps import radremap
        from wrfrun.run import WRFRun

        with WRFRun("config.toml"):
            radremap()
    """
    RadRemap(arps_source)()


def arpstrn():
    """
    Function interface for :class:`ARPSTrn`.

    Parameters needed to initialize :class:`ARPSTrn` is read from global variable :doc:`WRFRUN </api/core.core>`.
    """
    ARPSTrn()()


__all__ = ["arpssfc", "arps", "arps3dvar", "arpsintrp", "ext2arps", "radremap", "arpstrn"]
