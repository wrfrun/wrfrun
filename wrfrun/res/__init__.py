from os.path import abspath, dirname

from wrfrun.core import WRFRUNConfig


RES_PATH = abspath(dirname(__file__))
WRFRUNConfig.register_resource_uri(WRFRUNConfig.WRFRUN_RESOURCE_PATH, RES_PATH)

RUN_SH_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/run.template.sh"
EXT_NCL_PLOT_SCRIPT = ":WRFRUN_RESOURCE_PATH:/extension/plotgrids.ncl"
SCHEDULER_LSF_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/scheduler/lsf.template"
SCHEDULER_PBS_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/scheduler/pbs.template"
SCHEDULER_SLURM_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/scheduler/slurm.template"
NAMELIST_WRFDA = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.da_wrfvar.template"
NAMELIST_DFI = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.dfi.template"
NAMELIST_REAL = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.real.template"
NAMELIST_WRF = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.input.wrf.template"
NAMELIST_WPS = ":WRFRUN_RESOURCE_PATH:/namelist/namelist.wps.template"
CONFIG_MAIN_TOML_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/config/config.template.toml"
CONFIG_WRF_TOML_TEMPLATE = ":WRFRUN_RESOURCE_PATH:/config/wrf.template.toml"

WRFRUNConfig.set_config_template_path(CONFIG_MAIN_TOML_TEMPLATE)


__all__ = ["RUN_SH_TEMPLATE", "EXT_NCL_PLOT_SCRIPT", "SCHEDULER_LSF_TEMPLATE", "SCHEDULER_PBS_TEMPLATE", "SCHEDULER_SLURM_TEMPLATE", "NAMELIST_WRFDA", "NAMELIST_DFI", "NAMELIST_REAL", "NAMELIST_WRF", "NAMELIST_WPS", "CONFIG_MAIN_TOML_TEMPLATE", "CONFIG_WRF_TOML_TEMPLATE"]
