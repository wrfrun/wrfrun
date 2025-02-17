from os.path import abspath, dirname


_RES_PATH = abspath(dirname(__file__))
PBS_TEMPLATE = f"{_RES_PATH}/pbs.template"
SLURM_TEMPLATE = f"{_RES_PATH}/slurm.template"

__all__ = ["PBS_TEMPLATE", "SLURM_TEMPLATE"]
