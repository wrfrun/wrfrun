from os import listdir, remove, symlink
from os.path import abspath, basename, exists
from shutil import copyfile, move
from typing import Union

from wrfrun.core import WRFRUNConfig, WRFRUNConstants, register_custom_namelist_type, unregister_custom_namelist_type
from wrfrun.pbs import get_core_num
from wrfrun.utils import check_path, logger
from .core import exec_geogrid, exec_metgrid, exec_ndown, exec_real, exec_ungrib, exec_wrf
from .namelist import generate_namelist_file, prepare_dfi_namelist
from .utils import model_preprocess, model_postprocess, process_after_ndown, get_wif_dir, get_wif_prefix, reconcile_namelist_metgrid


def geogrid(geogrid_tbl_file: Union[str, None] = None):
    """
    Interface to execute geogrid.exe.
    This function is a higher interface of WPS,
    which will automatically check and prepare essential files, and save outputs.

    :param geogrid_tbl_file: Custom GEOGRID.TBL file path.
                             Defaults to None.
    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")

    model_preprocess("geogrid", WPS_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()
    output_save_path = f"{output_path}/geogrid"
    log_save_path = f"{output_path}/geogrid/logs"

    check_path(output_save_path, log_save_path)

    # check if we're going to use the custom GEOGRID.TBL file.
    if geogrid_tbl_file:

        # remove first
        remove(f"{WPS_WORK_PATH}/geogrid/GEOGRID.TBL")
        copyfile(geogrid_tbl_file, f"{WPS_WORK_PATH}/geogrid/GEOGRID.TBL")

    WRFRUNConstants.set_wrf_status("geogrid")

    generate_namelist_file("wps")

    exec_geogrid(get_core_num())

    model_postprocess(WPS_WORK_PATH, log_save_path, startswith="geogrid.log", copy_only=False, outputs="namelist.wps")
    model_postprocess(WPS_WORK_PATH, output_save_path, startswith="geo_em")

    # for _file in listdir(WPS_WORK_PATH):
    #     if _file.startswith("geogrid.log"):
    #         move(f"{WPS_WORK_PATH}/{_file}", f"{log_save_path}/{_file}")
    #     elif _file.startswith("geo_em"):
    #         copyfile(f"{WPS_WORK_PATH}/{_file}", f"{output_save_path}/{_file}")
    #
    # move(f"{WPS_WORK_PATH}/namelist.wps", f"{output_save_path}/namelist.wps")

    logger.info(f"All geogrid output files have been copied to {output_save_path}")


def ungrib(vtable_file: Union[str, None] = None):
    """
    Interface to execute ungrib.exe.
    This function is a higher interface of WPS,
    which will automatically check and prepare essential files, and save outputs.
    However, this function won't execute script "link_grib.csh", which will be executed in "exec_ungrib".

    :param vtable_file: Vtable file used to run ungrib.
                        Defaults to None.
    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")

    model_preprocess("ungrib", WPS_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()
    output_save_path = f"{output_path}/ungrib"
    log_save_path = f"{output_path}/ungrib/logs"

    check_path(output_save_path, log_save_path)

    input_data_path = WRFRUNConfig.get_wrf_config()["wps_input_data_folder"]

    # convert to an absolute path
    input_data_path = abspath(input_data_path)
    if vtable_file is not None:
        vtable_file = abspath(vtable_file)
    else:
        vtable_file = f"{WPS_WORK_PATH}/ungrib/Variable_Tables/Vtable.ERA-interim.pl"

    logger.info(f"Link vtable file: {vtable_file}")
    if exists(f"{WPS_WORK_PATH}/Vtable"):
        remove(f"{WPS_WORK_PATH}/Vtable")
    symlink(vtable_file, f"{WPS_WORK_PATH}/Vtable")

    WRFRUNConstants.set_wrf_status("ungrib")

    generate_namelist_file("wps")

    exec_ungrib(input_data_path)

    dir_name = get_wif_dir()
    file_prefix = get_wif_prefix()

    model_postprocess(dir_name, output_save_path, startswith=file_prefix)
    model_postprocess(WPS_WORK_PATH, log_save_path, outputs=["ungrib.log", "namelist.wps"], copy_only=False)

    # for _file in listdir(dir_name):
    #     if _file.startswith(file_prefix):
    #         copyfile(f"{dir_name}/{_file}", f"{output_save_path}/{_file}")
    #
    # move(f"{WPS_WORK_PATH}/ungrib.log", f"{log_save_path}/ungrib.log")
    # move(f"{WPS_WORK_PATH}/namelist.wps", f"{log_save_path}/namelist.wps")

    logger.info(f"All ungrib output files have been copied to {output_save_path}")


def metgrid():
    """
    Interface to execute metgrid.exe.
    This function is a higher interface of WPS,
    which will automatically check and prepare essential files, and save outputs.

    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    WPS_WORK_PATH = WRFRUNConstants.get_work_path("wps")

    model_preprocess("metgrid", WPS_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()
    output_save_path = f"{output_path}/metgrid"
    log_save_path = f"{output_path}/metgrid/logs"

    check_path(output_save_path, log_save_path)

    WRFRUNConstants.set_wrf_status("metgrid")

    generate_namelist_file("wps")

    exec_metgrid(get_core_num())

    model_postprocess(WPS_WORK_PATH, log_save_path, startswith="metgrid.log", outputs="namelist.wps", copy_only=False)
    model_postprocess(WPS_WORK_PATH, output_save_path, startswith="met_em", copy_only=False)

    # for _file in listdir(WPS_WORK_PATH):
    #     if _file.startswith("metgrid.log"):
    #         move(f"{WPS_WORK_PATH}/{_file}", f"{log_save_path}/{_file}")
    #     elif _file.startswith("met_em"):
    #         move(f"{WPS_WORK_PATH}/{_file}", f"{output_save_path}/{_file}")
    #
    # move(f"{WPS_WORK_PATH}/namelist.wps", f"{log_save_path}/namelist.wps")

    logger.info(f"All metgrid output files have been copied to {output_save_path}")


def real(metgrid_path: Union[str, None] = None):
    """
    Interface to execute real.exe.
    This function is a higher interface of WRF,
    which will automatically check and prepare essential files, and save outputs.

    :param metgrid_path: The path store output from metgrid.exe.
                         If it is None, the default output path will be used.
    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    model_preprocess("real", WRF_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()

    if metgrid_path is None:
        metgrid_path = f"{output_path}/metgrid"

    output_save_path = f"{output_path}/real"
    log_save_path = f"{output_path}/real/logs"

    check_path(output_save_path, log_save_path)

    if not exists(metgrid_path):
        logger.error(f"Can't find metgrid output: {metgrid_path}")
        raise FileNotFoundError(f"Can't find metgrid output: {metgrid_path}")

    metgrid_path = abspath(metgrid_path)

    reconcile_namelist_metgrid(metgrid_path)

    logger.info(f"Link metgrid outputs to WRF work dir...")
    for _file in listdir(metgrid_path):
        if _file.startswith("met_em"):
            if exists(f"{WRF_WORK_PATH}/{_file}"):
                remove(f"{WRF_WORK_PATH}/{_file}")
            symlink(f"{metgrid_path}/{_file}", f"{WRF_WORK_PATH}/{_file}")

    WRFRUNConstants.set_wrf_status("real")

    generate_namelist_file("wrf")

    exec_real(get_core_num())

    model_postprocess(WRF_WORK_PATH, output_save_path, startswith=("wrfbdy", "wrfinput", "wrflow"))
    model_postprocess(WRF_WORK_PATH, log_save_path, startswith="rsl.", outputs="namelist.input", copy_only=False)

    logger.info(f"All real output files have been copied to {output_save_path}")


def dfi(real_output_path: Union[str, None] = None, update_real_output=True):
    """
    Interface to execute wrf.exe to apply Digital Filter Initialization (dfi) to real.exe outputs.
    This function is a higher interface of WRF,
    which will automatically check and prepare essential files, and save outputs.

    :param real_output_path: The path store output results from real.exe.
                             Defaults to None.
    :param update_real_output: If True, replace real's output "wrfinput_d01" with the DFI's output.
                               The original "wrfinput_d01" will be renamed to "wrfinput_d01_before_dfi".
    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    # prepare namelist
    status = register_custom_namelist_type("dfi")
    if status:
        prepare_dfi_namelist()

    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    model_preprocess("dfi", WRF_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()

    if real_output_path is None:
        real_output_path = WRF_WORK_PATH
    else:
        real_output_path = abspath(real_output_path)

    output_save_path = f"{output_path}/dfi"
    log_save_path = f"{output_path}/dfi/logs"

    check_path(output_save_path, log_save_path)

    if real_output_path != WRF_WORK_PATH:
        for _file in listdir(real_output_path):
            if exists(f"{WRF_WORK_PATH}/{_file}"):
                remove(f"{WRF_WORK_PATH}/{_file}")
            symlink(f"{real_output_path}/{_file}", f"{WRF_WORK_PATH}/{_file}")

    WRFRUNConstants.set_wrf_status("dfi")

    generate_namelist_file("dfi", f"{WRF_WORK_PATH}/namelist.input")

    exec_wrf(get_core_num())

    model_postprocess(WRF_WORK_PATH, log_save_path, startswith="rsl.", outputs="namelist.input", copy_only=False)
    model_postprocess(WRF_WORK_PATH, output_save_path, outputs="wrfinput_initialized_d01")

    if update_real_output:
        move(f"{real_output_path}/wrfinput_d01", f"{real_output_path}/wrfinput_d01_before_dfi")
        copyfile(f"{output_save_path}/wrfinput_initialized_d01", f"{real_output_path}/wrfinput_d01")
        logger.info(f"Replace real's output \"wrfinput_d01\" with output, old file has been renamed as \"wrfinput_d01_before_dfi\"")

    logger.info(f"All DFI output files have been copied to {output_save_path}")

    unregister_custom_namelist_type("dfi")


def wrf(wrf_input_path: Union[str, None] = None):
    """
    Interface to execute wrf.exe.
    This function is a higher interface of WRF,
    which will automatically check and prepare essential files, and save outputs.

    :param wrf_input_path: The path store input data which will be feed into wrf.exe.
                           Defaults to None.
    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    model_preprocess("wrf", WRF_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()

    if wrf_input_path is None:
        wrf_input_path = WRF_WORK_PATH
    else:
        wrf_input_path = abspath(wrf_input_path)

    output_save_path = f"{output_path}/wrf"
    log_save_path = f"{output_path}/wrf/logs"

    check_path(output_save_path, log_save_path)

    if wrf_input_path != WRF_WORK_PATH:
        for _file in listdir(wrf_input_path):
            if exists(f"{WRF_WORK_PATH}/{_file}"):
                remove(f"{WRF_WORK_PATH}/{_file}")
            symlink(f"{wrf_input_path}/{_file}", f"{WRF_WORK_PATH}/{_file}")

    WRFRUNConstants.set_wrf_status("wrf")

    generate_namelist_file("wrf")

    exec_wrf(get_core_num())

    model_postprocess(WRF_WORK_PATH, log_save_path, startswith="rsl.", outputs="namelist.input", copy_only=False)
    model_postprocess(WRF_WORK_PATH, output_save_path, startswith="wrfout")

    logger.info(f"All wrf output files have been copied to {output_save_path}")


def ndown(wrfout_file_path: str, wrfinput_file_path: str, update_namelist=True):
    """
    Interface to execute ndown.exe.
    This function is a higher interface of WRF,
    which will automatically check and prepare essential files, and save outputs.

    :param wrfout_file_path: The output file from a coarse grid WRF simulation.
    :param wrfinput_file_path: The higher resolution output file from real.exe.
    :param update_namelist: If True, function `process_after_ndown` will be called to update namelist.
    """
    WRFRUNConstants.check_wrfrun_context(error=True)

    if not exists(wrfout_file_path):
        logger.error(f"wrfout file not found: {wrfout_file_path}")
        raise FileNotFoundError(f"wrfout file not found: {wrfout_file_path}")

    if not exists(wrfinput_file_path):
        logger.error(f"wrfinput file not found: {wrfinput_file_path}")
        raise FileNotFoundError(f"wrfinput file not found: {wrfinput_file_path}")

    wrfout_file_path = abspath(wrfout_file_path)
    wrfinput_file_path = abspath(wrfinput_file_path)

    WRF_WORK_PATH = WRFRUNConstants.get_work_path("wrf")

    model_preprocess("ndown", WRF_WORK_PATH)

    output_path = WRFRUNConfig.get_output_path()

    output_save_path = f"{output_path}/ndown"
    log_save_path = f"{output_path}/ndown/logs"

    check_path(output_save_path, log_save_path)

    logger.info(f"Use file {basename(wrfout_file_path)} as wrfout_d01")
    if exists(f"{WRF_WORK_PATH}/wrfout_d01"):
        remove(f"{WRF_WORK_PATH}/wrfout_d01")
    symlink(f"{wrfout_file_path}", f"{WRF_WORK_PATH}/wrfout_d01")

    logger.info(f"Use file {basename(wrfinput_file_path)} as wrfndi_d02")
    if exists(f"{WRF_WORK_PATH}/wrfndi_d02"):
        remove(f"{WRF_WORK_PATH}/wrfndi_d02")
    symlink(f"{wrfinput_file_path}", f"{WRF_WORK_PATH}/wrfndi_d02")

    WRFRUNConstants.set_wrf_status("ndown")

    exec_ndown(get_core_num())

    model_postprocess(WRF_WORK_PATH, log_save_path, startswith="rsl.", outputs="namelist.input", copy_only=False)

    logger.info(f"Rename ndown output `wrfinput_d02` to `wrfinput_d01`")
    move(f"{WRF_WORK_PATH}/wrfinput_d02", f"{output_save_path}/wrfinput_d01")

    logger.info(f"Rename ndown output `wrfbdy_d02` to `wrfbdy_d01`")
    move(f"{WRF_WORK_PATH}/wrfbdy_d02", f"{output_save_path}/wrfbdy_d01")

    logger.info(f"All ndown output files have been copied to {output_save_path}")

    if update_namelist:
        process_after_ndown()


__all__ = ["geogrid", "ungrib", "metgrid", "real", "wrf", "ndown", "dfi"]
