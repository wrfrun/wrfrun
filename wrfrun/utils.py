"""
wrfrun.utils
############

.. autosummary::
    :toctree: generated/

    check_path
    rectify_domain_size
    _calculate_domain_shape
    calculate_domain_shape
    _check_domain_shape
    check_domain_shape

Utility submodule.
"""

from os import makedirs
from os.path import exists
from shutil import rmtree


def check_path(*args, force=False):
    """
    Check and create all the path in args.

    :param args: Path list.
    :type args: list[str]
    :param force: If ``True``, delete existed directory and create a new.
    :type force: bool
    """
    for _path in args:
        if exists(_path) and force:
            rmtree(_path)
        if not exists(_path):
            makedirs(_path)


def rectify_domain_size(point_num: int, nest_ratio: int) -> int:
    """
    Rectify domain size.

    :param point_num: Point number of one side.
    :type point_num: int
    :param nest_ratio: The nesting ratio relative to the domain's parent.
    :type nest_ratio: int
    :return: New size.
    :rtype: int
    """
    # calculate remainder
    point_num_mod = (point_num - 1) % nest_ratio

    if point_num_mod == 0:
        return point_num

    if point_num_mod < nest_ratio / 2:
        # # point_num_mod is closer to (nest_ratio - 1) than nest_ratio
        point_num -= point_num_mod
    else:
        # # point_num_mod is closer to nest_ratio than (nest_ratio - 1)
        point_num += nest_ratio - point_num_mod

    return point_num


def _calculate_domain_shape(step: float, resolution: int, grid_resolution=110, nest_ratio=1) -> int:
    """
    Calculate domain shape based on its area.

    :param step: Length of the side. Unit: degree.
    :type step: float
    :param resolution: Resolution of domain. Unit: km.
    :type resolution: int
    :param grid_resolution: Resolution of grid. Unit: km. Defaults to 110.
    :param nest_ratio: The nesting ratio relative to the domain’s parent.
    :return: ``(length of x, length of y)``.
    :rtype: int
    """
    # calculate res based on doamin area and resolution
    res = int(step * grid_resolution) // resolution

    # rectify

    return rectify_domain_size(res, nest_ratio=nest_ratio)


def calculate_domain_shape(
    lon_step: float, lat_step: float, resolution: int, grid_resolution=110, nest_ratio=1
) -> tuple[int, int]:
    """
    Calculate domain shape based on its area.

    :param lon_step: Length in X direction. Unit: degree.
    :type lon_step: float
    :param lat_step: Length in Y direction. Unit: degree.
    :type lat_step: float
    :param resolution: Resolution of domain. Unit: km.
    :type resolution: int
    :param grid_resolution: Resolution of grid. Unit: km. Defaults to 110.
    :param nest_ratio: The nesting ratio relative to the domain’s parent.
    :return: ``(length of x, length of y)``.
    :rtype: tuple[int, int]
    """
    return (
        _calculate_domain_shape(lon_step, resolution, grid_resolution=grid_resolution, nest_ratio=nest_ratio),
        _calculate_domain_shape(lat_step, resolution, grid_resolution=grid_resolution, nest_ratio=nest_ratio),
    )


def _check_domain_shape(point_num: int, nest_ratio: int) -> bool:
    """
    Check domain shape.

    :param point_num: Point number of one side.
    :type point_num: int
    :param nest_ratio: The nesting ratio relative to the domain’s parent.
    :type nest_ratio: int
    :return: True if pass check else False.
    :rtype: bool
    """
    if (point_num - 1) % nest_ratio != 0:
        return False
    else:
        return True


def check_domain_shape(x_point_num: int, y_point_num: int, nest_ratio: int) -> tuple[bool, bool]:
    """
    Check domain shape.

    :param x_point_num: Point number of X side.
    :type x_point_num: int
    :param y_point_num: Point number of Y side.
    :type y_point_num: int
    :param nest_ratio: The nesting ratio relative to the domain's parent.
    :type nest_ratio: int
    :return: Tuple of bool. True if pass check else False
    :rtype: tuple[bool, bool]
    """
    return (
        _check_domain_shape(x_point_num, nest_ratio=nest_ratio),
        _check_domain_shape(y_point_num, nest_ratio=nest_ratio),
    )


__all__ = [
    "check_path",
    "calculate_domain_shape",
    "rectify_domain_size",
    "check_domain_shape",
]
