"""
This module provides the lower interface to WPS and WRF executable files.
"""

from typing import Optional

from wrfrun.core import WRFRUNConstants
from wrfrun.utils import call_subprocess, logger


def exec_geogrid(core_num: Optional[int] = None):
    """
    A lower interface to run geogrid.
    You should have prepared the ``namelist.wps`` file before calling this function, because it doesn't have the function to prepare the ``namelist.wps`` file.

    Args:
        core_num: An positive integer number of used core numbers.
                  mpirun will be used to execute geogrid.exe if ``core_num != None``.

    """
    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")

    if isinstance(core_num, int) and core_num <= 0:
        logger.warning(f"`core_num` should be greater than 0")
        core_num = None

    if core_num is None:
        logger.info(f"Running `./geogrid.exe` ...")
        call_subprocess(["./geogrid.exe"], work_path=WPS_WORK_PATH)
    else:
        logger.info(f"Running `mpirun -np {core_num} geogrid.exe` ...")
        call_subprocess(["mpirun", "-np", str(core_num), "./geogrid.exe"], work_path=WPS_WORK_PATH)


def exec_ungrib(grib_dir_path: str):
    """
    A lower interface to run ungrib.
    It will execute "link_grib.csh" script of WPS to create symbol links to GRIB files before execute "ungrib.exe",
    but you also should have prepared the ``namelist.wps`` file before calling this function,
    because it doesn't have the function to prepare the ``namelist.wps`` file.

    Args:
        grib_dir_path: Absolute directory path of GRIB files.

    """
    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")

    logger.info(f"Running `./link_grib.csh {grib_dir_path}/* .` ...")
    call_subprocess(["./link_grib.csh", f"{grib_dir_path}/*", "."], work_path=WPS_WORK_PATH)

    logger.info(f"Running `./ungrib.exe` ...")
    call_subprocess(["./ungrib.exe"], work_path=WPS_WORK_PATH)


def exec_metgrid(core_num: Optional[int] = None):
    """
    A lower interface to run metgrid.
    You should have prepared the ``namelist.wps`` file before calling this function, because it doesn't have the function to prepare the ``namelist.wps`` file.

    Args:
        core_num: An positive integer number of used core numbers.
                  mpirun will be used to execute geogrid.exe if ``core_num != None``.

    """
    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")

    if isinstance(core_num, int) and core_num <= 0:
        logger.warning(f"`core_num` should be greater than 0")
        core_num = None

    if core_num is None:
        logger.info(f"Running `./metgrid.exe` ...")
        call_subprocess(["./metgrid.exe"], work_path=WPS_WORK_PATH)
    else:
        logger.info(f"Running `mpirun -np {core_num} metgrid.exe` ...")
        call_subprocess(["mpirun", "-np", str(core_num), "./metgrid.exe"], work_path=WPS_WORK_PATH)


def exec_ndown(core_num: Optional[int] = None):
    """
    A lower interface to run ndown.
    You should have prepared the ``namelist.input`` file before calling this function, because it doesn't have the function to prepare the ``namelist.input`` file.
    
    Args:
        core_num: An positive integer number of used core numbers.
                  mpirun will be used to execute geogrid.exe if ``core_num != None``.

    """
    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    if isinstance(core_num, int) and core_num <= 0:
        logger.warning(f"`core_num` should be greater than 0")
        core_num = None

    if core_num is None:
        logger.info(f"Running `./ndown.exe` ...")
        call_subprocess(["./ndown.exe"], work_path=WRF_WORK_PATH)
    else:
        logger.info(f"Running `mpirun -np {core_num} ./ndown.exe` ...")
        call_subprocess(["mpirun", "-np", str(core_num), "./ndown.exe"], work_path=WRF_WORK_PATH)


def exec_real(core_num: Optional[int] = None):
    """
    A lower interface to run real.
    You should have prepared the ``namelist.input`` file before calling this function, because it doesn't have the function to prepare the ``namelist.input`` file.
    
    Args:
        core_num: An positive integer number of used core numbers.
                  mpirun will be used to execute geogrid.exe if ``core_num != None``.

    """
    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    if isinstance(core_num, int) and core_num <= 0:
        logger.warning(f"`core_num` should be greater than 0")
        core_num = None

    if core_num is None:
        logger.info(f"Running `./real.exe` ...")
        call_subprocess(["./real.exe"], work_path=WRF_WORK_PATH)
    else:
        logger.info(f"Running `mpirun -np {core_num} real.exe` ...")
        call_subprocess(["mpirun", "-np", str(core_num), "./real.exe"], work_path=WRF_WORK_PATH)


def exec_wrf(core_num: Optional[int] = None):
    """
    A lower interface to run wrf.
    You should have prepared the ``namelist.input`` file before calling this function, because it doesn't have the function to prepare the ``namelist.input`` file.
    
    Args:
        core_num: An positive integer number of used core numbers.
                  mpirun will be used to execute geogrid.exe if ``core_num != None``.

    """
    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    if isinstance(core_num, int) and core_num <= 0:
        logger.warning(f"`core_num` should be greater than 0")
        core_num = None

    if core_num is None:
        logger.info(f"Running `./wrf.exe` ...")
        call_subprocess(["./wrf.exe"], work_path=WRF_WORK_PATH)
    else:
        logger.info(f"Running `mpirun -np {core_num} wrf.exe` ...")
        call_subprocess(["mpirun", "-np", str(core_num), "./wrf.exe"], work_path=WRF_WORK_PATH)


def exec_da_wrfvar(core_num: Optional[int] = None):
    """
    A lower interface to run da_wrfvar.
    You should have prepared the ``namelist.input`` and ``param.in`` file before calling this function,
    because it doesn't have the function to prepare the ``namelist.input`` and ``param.in`` file.
    
    Args:
        core_num: An positive integer number of used core numbers.
                  mpirun will be used to execute geogrid.exe if ``core_num != None``.

    """
    WRFDA_WORK_PATH = WRFRUNConstants.get_work_path("wrfda")

    if isinstance(core_num, int) and core_num <= 0:
        logger.warning(f"`core_num` should be greater than 0")
        core_num = None

    if core_num is None:
        logger.info(f"Running `./da_wrfvar.exe` ...")
        call_subprocess(["./da_wrfvar.exe"], work_path=WRFDA_WORK_PATH)
    else:
        logger.info(f"Running `mpirun -np {core_num} da_wrfvar.exe` ...")
        call_subprocess(["mpirun", "-np", str(core_num), "./da_wrfvar.exe"], work_path=WRFDA_WORK_PATH)


def exec_da_update_bc():
    """A lower interface to run da_update_bc.

    """
    WRFDA_WORK_PATH = WRFRUNConstants.get_work_path("wrfda")

    logger.info(
        f"Running `./da_update_bc.exe` ...")
    call_subprocess(["./da_update_bc.exe"], work_path=WRFDA_WORK_PATH)


__all__ = ["exec_geogrid", "exec_ungrib", "exec_metgrid", "exec_real", "exec_wrf", "exec_ndown", "exec_da_wrfvar", "exec_da_update_bc"]
