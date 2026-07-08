"""
wrfrun.model.arps.core
######################

Core implementation of ARPS model.

If you prefer function interfaces, please see :doc:`function wrapper </api/model.wrf.exec_wrap>` for these ``Executable``.

.. autosummary::
    :toctree: generated/

    GeoGrid
    LinkGrib
    UnGrib
    MetGrid
    Real
    WRF
    DFI
    NDown
"""

from wrfrun.core import WRFRUN, ExecutableBase
from wrfrun.workspace.arps import get_arps_workspace_path


def _check_and_prepare_namelist():
    wrfrun_config = WRFRUN.config

    if not wrfrun_config.check_namelist("arps"):
        prepare_arps_namelist()


class ARPSSFC(ExecutableBase):
    """
    ``Executable`` for "arpssfc".

    .. py:attribute:: work_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of arpssfc workspace path.

    .. py:attribute:: namelist_path
        :type: str
        :value: Internal URI.

        Internal URI which represents the absolute path of arpssfc namelist path.
    """

    def __init__(self):
        """
        ``Executable`` for "arpssfc".
        """
        mpi_use = False
        mpi_cmd = None
        mpi_core_num = None

        self.work_path = f"{get_arps_workspace_path()}/arpssfc"
        self.namelist_path = f"{self.work_path}/arpssfc.nml"

        super().__init__(
            name="arpssfc",
            cmd="./arpssfc",
            work_path=self.work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )
