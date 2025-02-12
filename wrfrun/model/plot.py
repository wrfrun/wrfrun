from os import getcwd, chdir
from os.path import abspath, exists
from shutil import copyfile, move

from wrfrun.core import WRFRUNConfig, WRFRUNConstants, WRFRUNNamelist
from wrfrun.res import NCL_PLOT_SCRIPT
from wrfrun.utils import check_path, call_subprocess, logger


def plot_domain_area():
    """Generate namelist and plot domain area with WRF NCL script.

    """
    # get save path
    save_path = WRFRUNConfig.get_output_path()

    # check
    check_path(save_path)

    # conver to absolute path
    save_path = abspath(save_path)
    save_path = f"{save_path}/wps_show_dom.png"

    # record original path
    origin_path = getcwd()

    # enter WPS WORK PATH
    chdir(WRFRUNConstants.get_work_path("wps"))

    # save namelist
    WRFRUNNamelist.write_namelist("./namelist.wps", "wps", overwrite=True)

    # copy plot script and plot
    copyfile(NCL_PLOT_SCRIPT, f"./plotgrids.ncl")
    call_subprocess(["ncl", "./plotgrids.ncl"], print_output=True)

    # save image
    # we need to check image file, because sometimes ncl doesn't return error code
    if not exists("./wps_show_dom.png"):
        logger.error(f"Fail to plot domain with NCL. Check the log above")
        raise FileNotFoundError
    move("./wps_show_dom.png", save_path)

    logger.info(f"The image of domain area has been saved to {save_path}")

    # go back
    chdir(origin_path)


__all__ = ["plot_domain_area"]
