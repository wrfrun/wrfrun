from os.path import basename
from typing import Optional, Union

from wrfrun import WRFRUNConfig
from .core import DFI, GeoGrid, MetGrid, Real, UnGrib, WRF, NDown


def geogrid(geogrid_tbl_file: Union[str, None] = None):
    """
    Interface to execute geogrid.exe.

    :param geogrid_tbl_file: Custom GEOGRID.TBL file path. Defaults to None.
    """
    GeoGrid(geogrid_tbl_file, WRFRUNConfig.get_core_num())()


def ungrib(vtable_file: Union[str, None] = None, input_data_path: Optional[str] = None, prefix="FILE"):
    """
    Interface to execute ungrib.exe.

    :param vtable_file: Vtable file used to run ungrib. Defaults to None.
    :type vtable_file: str
    :param input_data_path: Directory path of the input data. If None, ``wrfrun`` will read its value from the config file.
    :type input_data_path: str
    :param prefix: Prefix of ungrib output.
    :type prefix: str
    """
    prefix = basename(prefix)
    WRFRUNConfig.set_ungrib_out_prefix(prefix)

    UnGrib(vtable_file, input_data_path)()


def metgrid(geogrid_data_path: Optional[str] = None, ungrib_data_path: Optional[str] = None, fg_names: Union[str, list[str]] = "FILE"):
    """
    Interface to execute metgrid.exe.

    :param geogrid_data_path: Directory path of outputs from geogrid.exe. If None, tries to use the output path specified by config file.
    :type geogrid_data_path: str
    :param ungrib_data_path: Directory path of outputs from ungrib.exe. If None, tries to use the output path specified by config file.
    :type ungrib_data_path: str
    :param fg_names: Set ``fg_name`` of metgrid, a single prefix string or a string list.
    :type fg_names: str | list
    """
    if isinstance(fg_names, str):
        fg_names = [fg_names, ]
    fg_names = [basename(x) for x in fg_names]
    WRFRUNConfig.set_metgrid_fg_names(fg_names)

    MetGrid(geogrid_data_path, ungrib_data_path, WRFRUNConfig.get_core_num())()


def real(metgrid_data_path: Union[str, None] = None):
    """
    Interface to execute real.exe.

    :param metgrid_data_path: The path store output from metgrid.exe. If it is None, the default output path will be used.
    """
    Real(metgrid_data_path, WRFRUNConfig.get_core_num())()


def wrf(input_file_dir_path: Union[str, None] = None, restart_file_dir_path: Optional[str] = None, save_restarts=False):
    """
    Interface to execute wrf.exe.

    :param input_file_dir_path: The path store input data which will be feed into wrf.exe. Defaults to None.
    :param restart_file_dir_path: The path store WRF restart files. This parameter will be ignored if ``restart=False`` in your config.
    :param save_restarts: Also save restart files to the output directory.
    """
    WRF(input_file_dir_path, restart_file_dir_path, save_restarts, WRFRUNConfig.get_core_num())()


def dfi(input_file_dir_path: Optional[str] = None, update_real_output=True):
    """
    Execute "wrf.exe" to run DFI.

    :param input_file_dir_path: Path of the directory that stores input data for "wrf.exe".
    :type input_file_dir_path: str
    :param update_real_output: If update the corresponding file in real.exe output directory.
    :type update_real_output: bool
    """
    DFI(input_file_dir_path, update_real_output, WRFRUNConfig.get_core_num())()


def ndown(wrfout_file_path: str, real_output_dir_path: Optional[str] = None, update_namelist=True):
    """
    Execute "ndown.exe".

    :param wrfout_file_path: wrfout file path.
    :type wrfout_file_path: str
    :param real_output_dir_path: Path of the directory that contains output of "real.exe".
    :type real_output_dir_path: str
    :param update_namelist: If update wrf's namelist for the final integral.
    :type update_namelist: bool
    :return:
    :rtype:
    """
    NDown(wrfout_file_path, real_output_dir_path, update_namelist, WRFRUNConfig.get_core_num())()


__all__ = ["geogrid", "ungrib", "metgrid", "real", "wrf", "dfi", "ndown"]
