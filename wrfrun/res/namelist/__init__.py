from os.path import abspath, dirname


# get resource file path
RES_PATH = abspath(dirname(__file__))
NAMELIST_WPS_TEMPLATE = f"{RES_PATH}/namelist.wps.template"
NAMELIST_WRF_TEMPLATE = f"{RES_PATH}/namelist.input.wrf.template"
NAMELIST_REAL_TEMPLATE = f"{RES_PATH}/namelist.input.real.template"
NAMELIST_DA_WRFVAR_TEMPLATE = f"{RES_PATH}/namelist.input.da_wrfvar.template"
NAMELIST_DFI_TEMPLATE = f"{RES_PATH}/namelist.input.dfi.template"
NAMELIST_PARAME_IN_TEMPLATE = f"{RES_PATH}/parame.in.template"


__all__ = ["NAMELIST_WPS_TEMPLATE", "NAMELIST_WRF_TEMPLATE",
           "NAMELIST_REAL_TEMPLATE", "NAMELIST_DA_WRFVAR_TEMPLATE",
           "NAMELIST_DFI_TEMPLATE", "NAMELIST_PARAME_IN_TEMPLATE"]
