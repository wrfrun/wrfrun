from os.path import abspath, dirname


RES_PATH = abspath(dirname(__file__))
GEOGRID_SHANDONG_LANDUSE_SOIL_TOP = f"{RES_PATH}/GEOGRID.SHAN_DONG_LANDUSE_SOIL_TOP.TBL"


__all__ = ["GEOGRID_SHANDONG_LANDUSE_SOIL_TOP"]
