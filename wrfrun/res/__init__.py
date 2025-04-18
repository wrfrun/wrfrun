from os.path import abspath, dirname

from wrfrun.core import WRFRUNConfig


RES_PATH = abspath(dirname(__file__))
WRFRUNConfig.register_resource_uri(WRFRUNConfig.WRFRUN_RESOURCE_PATH, RES_PATH)

CONFIG_TOML_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/config.toml.template"
EXT_NCL_PLOT_SCRIPT = ":WRFRUN_RESOURCE_PATH:/extension/plotgrids.ncl"
TASKSYS_PBS_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/job_scheduler/pbs.template"
TASKSYS_SLURM_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/job_scheduler/slurm.template"
NAMELIST_WRFDA = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.da_wrfvar.template"
NAMELIST_DFI = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.dfi.template"
NAMELIST_REAL = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.real.template"
NAMELIST_WRF = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.wrf.template"
NAMELIST_WPS = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.wps.template"

WRFRUNConfig.set_config_template_path(CONFIG_TOML_TEMPLATE)


__all__ = ["CONFIG_TOML_TEMPLATE", "EXT_NCL_PLOT_SCRIPT", "TASKSYS_PBS_TEMPLATE", "TASKSYS_SLURM_TEMPLATE", "NAMELIST_WRFDA", "NAMELIST_DFI", "NAMELIST_REAL", "NAMELIST_WRF", "NAMELIST_WPS"]
