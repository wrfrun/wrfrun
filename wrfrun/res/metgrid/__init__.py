from os.path import abspath, dirname


RES_PATH = abspath(dirname(__file__))
METGRID_TBL = f"{RES_PATH}/METGRID.TBL"


__all__ = ["METGRID_TBL"]
