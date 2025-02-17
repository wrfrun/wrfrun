from os.path import abspath, dirname

from .extension import *
from .geogrid import *
from .namelist import *
from .ungrib import *
from .job_scheduler import *


_RES_PATH = abspath(dirname(__file__))
METGRID_DEFAULT_TBL = f"{_RES_PATH}/metgrid/METGRID.TBL"
CONFIG_TEMPLATE = f"{_RES_PATH}/config.yaml.template"
PBS_SCRIPT_TEMPLATE = f"{_RES_PATH}/run.sh.template"
