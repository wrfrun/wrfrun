"""
wrfrun.model.wrf.exec_wrap
##########################

Function wrapper of WPS / WRF :doc:`Executables </api/model.wrf.core>`.

.. autosummary::
    :toctree: generated/

    geogrid
    ungrib
    metgrid
    real
    wrf
    dfi
    ndown
"""

from typing import Optional, Union

from wrfrun import WRFRUNConfig
from .core import DFI, GeoGrid, MetGrid, NDown, Real, UnGrib, WRF


def geogrid(geogrid_tbl_file: Union[str, None] = None):
    """
    Function interface for :class:`GeoGrid <wrfrun.model.wrf.core.GeoGrid>`.

    :param geogrid_tbl_file: Custom GEOGRID.TBL file path. Defaults to None.
    """
    GeoGrid(geogrid_tbl_file, WRFRUNConfig.get_core_num())()


def ungrib(vtable_file: Union[str, None] = None, input_data_path: Optional[str] = None, prefix="FILE"):
    """
    Function interface for :class:`UnGrib <wrfrun.model.wrf.core.UnGrib>`.

    :param vtable_file: Path of the Vtable file.
                        Defaults to :attr:`VtableFiles.ERA_PL <vtable.VtableFiles.ERA_PL>`.
    :type vtable_file: str
    :param input_data_path: Directory path of input GRIB files.
                            Defaults to ``input_data_path`` set in user's config file.
    :type input_data_path: str
    :param prefix: Prefix of outputs.
    :type prefix: str
    """
    UnGrib(vtable_file, input_data_path).set_ungrib_output_prefix(prefix)()


def metgrid(geogrid_data_path: Optional[str] = None, ungrib_data_path: Optional[str] = None, fg_names: Union[str, list[str]] = "FILE"):
    """
    Function interface for :class:`MetGrid <wrfrun.model.wrf.core.MetGrid>`.

    :param geogrid_data_path: Directory path of :class:`GeoGrid <wrfrun.model.wrf.core.GeoGrid>` outputs.
                              If is ``None``, try to use the output path specified by config file.
    :type geogrid_data_path: str
    :param ungrib_data_path: Directory path of :class:`UnGrib <wrfrun.model.wrf.core.UnGrib>` outputs.
                             If is ``None``, try to use the output path specified by config file.
    :type ungrib_data_path: str
    :param fg_names: ``fg_name`` of metgrid, a single prefix string or a string list.
    :type fg_names: str | list
    """
    MetGrid(
        geogrid_data_path, ungrib_data_path, WRFRUNConfig.get_core_num()
    ).set_metgrid_fg_names(fg_names)()


def real(metgrid_data_path: Union[str, None] = None):
    """
    Function interface for :class:`Real <wrfrun.model.wrf.core.Real>`.

    :param metgrid_data_path: Directory path of :class:`MetGrid <wrfrun.model.wrf.core.MetGrid>` outputs.
                              If is ``None``, try to use the workspace path or output path in the config file.
    """
    Real(metgrid_data_path, WRFRUNConfig.get_core_num())()


def wrf(input_file_dir_path: Union[str, None] = None, restart_file_dir_path: Optional[str] = None, save_restarts=False):
    """
    Function interface for :class:`WRF <wrfrun.model.wrf.core.WRF>`.

    :param input_file_dir_path: Directory path of input data.
    :param restart_file_dir_path: Directory path of restart files.
    :param save_restarts: If saving restart files. Defaults to False.
    """
    WRF(input_file_dir_path, restart_file_dir_path, save_restarts, WRFRUNConfig.get_core_num())()


def dfi(input_file_dir_path: Optional[str] = None, update_real_output=True):
    """
    Function interface for :class:`DFI <wrfrun.model.wrf.core.DFI>`.

    :param input_file_dir_path: Directory path of input data.
    :type input_file_dir_path: str
    :param update_real_output: If update corresponding files in :class:`Real <wrfrun.model.wrf.core.Real>` outputs.
    :type update_real_output: bool
    """
    DFI(input_file_dir_path, update_real_output, WRFRUNConfig.get_core_num())()


def ndown(wrfout_file_path: str, real_output_dir_path: Optional[str] = None, update_namelist=True):
    """
    Function interface for :class:`NDown <wrfrun.model.wrf.core.NDown>`.

    :param wrfout_file_path: wrfout file path.
    :type wrfout_file_path: str
    :param real_output_dir_path: Directory path of :class:`Real <wrfrun.model.wrf.core.Real>` outputs.
    :type real_output_dir_path: str
    :param update_namelist: If update namelist settings for the final integral.
    :type update_namelist: bool
    """
    NDown(wrfout_file_path, real_output_dir_path, update_namelist, WRFRUNConfig.get_core_num())()


__all__ = ["geogrid", "ungrib", "metgrid", "real", "wrf", "dfi", "ndown"]
