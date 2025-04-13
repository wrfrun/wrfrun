from os import listdir, remove, symlink
from os.path import abspath, basename, exists
from shutil import copyfile, move
from typing import Union

from wrfrun.core import WRFRUNConfig
from wrfrun.pbs import get_core_num
from wrfrun.utils import check_path, logger
from .core import exec_ndown, exec_wrf
from .namelist import prepare_dfi_namelist
from .dutils import model_preprocess, model_postprocess, process_after_ndown


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
    WRFRUNConfig.check_wrfrun_context(error=True)

    # prepare namelist
    status = WRFRUNConfig.register_custom_namelist_id("dfi")
    if status:
        prepare_dfi_namelist()

    WRF_WORK_PATH = WRFRUNConfig.WRF_WORK_PATH

    model_preprocess("dfi", WRF_WORK_PATH)

    output_path = WRFRUNConfig.WRFRUN_OUTPUT_PATH

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

    WRFRUNConfig.set_work_status("dfi")

    WRFRUNConfig.write_namelist(f"{WRF_WORK_PATH}/namelist.input", "dfi")

    exec_wrf(get_core_num())

    model_postprocess(WRF_WORK_PATH, log_save_path, startswith="rsl.", outputs="namelist.input", copy_only=False)
    model_postprocess(WRF_WORK_PATH, output_save_path, outputs="wrfinput_initialized_d01")

    if update_real_output:
        move(f"{real_output_path}/wrfinput_d01", f"{real_output_path}/wrfinput_d01_before_dfi")
        copyfile(f"{output_save_path}/wrfinput_initialized_d01", f"{real_output_path}/wrfinput_d01")
        logger.info(f"Replace real's output \"wrfinput_d01\" with output, old file has been renamed as \"wrfinput_d01_before_dfi\"")

    logger.info(f"All DFI output files have been copied to {output_save_path}")

    WRFRUNConfig.unregister_custom_namelist_id("dfi")


def ndown(wrfout_file_path: str, wrfinput_file_path: str, update_namelist=True):
    """
    Interface to execute ndown.exe.
    This function is a higher interface of WRF,
    which will automatically check and prepare essential files, and save outputs.

    :param wrfout_file_path: The output file from a coarse grid WRF simulation.
    :param wrfinput_file_path: The higher resolution output file from real.exe.
    :param update_namelist: If True, function `process_after_ndown` will be called to update namelist.
    """
    WRFRUNConfig.check_wrfrun_context(error=True)

    if not exists(wrfout_file_path):
        logger.error(f"wrfout file not found: {wrfout_file_path}")
        raise FileNotFoundError(f"wrfout file not found: {wrfout_file_path}")

    if not exists(wrfinput_file_path):
        logger.error(f"wrfinput file not found: {wrfinput_file_path}")
        raise FileNotFoundError(f"wrfinput file not found: {wrfinput_file_path}")

    wrfout_file_path = abspath(wrfout_file_path)
    wrfinput_file_path = abspath(wrfinput_file_path)

    WRF_WORK_PATH = WRFRUNConfig.WRF_WORK_PATH

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

    WRFRUNConfig.WRFRUN_WORK_STATUS = "ndown"

    exec_ndown(get_core_num())

    model_postprocess(WRF_WORK_PATH, log_save_path, startswith="rsl.", outputs="namelist.input", copy_only=False)

    logger.info(f"Rename ndown output `wrfinput_d02` to `wrfinput_d01`")
    move(f"{WRF_WORK_PATH}/wrfinput_d02", f"{output_save_path}/wrfinput_d01")

    logger.info(f"Rename ndown output `wrfbdy_d02` to `wrfbdy_d01`")
    move(f"{WRF_WORK_PATH}/wrfbdy_d02", f"{output_save_path}/wrfbdy_d01")

    logger.info(f"All ndown output files have been copied to {output_save_path}")

    if update_namelist:
        process_after_ndown()


__all__ = ["ndown", "dfi"]
