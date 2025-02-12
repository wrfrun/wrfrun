from os.path import abspath, dirname


_PATH = abspath(dirname(__file__))

NCL_PLOT_SCRIPT = f"{_PATH}/plotgrids.ncl"


__all__ = ["NCL_PLOT_SCRIPT"]
