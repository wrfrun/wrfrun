"""
wrfrun.model.type
#################

Definition of types used in ``wrfrun.model``.

.. autosummary::
    :toctree: generated/

    DomainSetting
"""

from typing import Literal, TypedDict, Union


class DomainSetting(TypedDict):
    """
    Domain settings which can be used to create a projection.

    .. py:attribute:: resolution_x
        :type: int

        Spacing of the domain 1 grid points along the longitude direction, unit: meter.

    .. py:attribute:: resolution_y
        :type: int

        Spacing of the domain 1 grid points along the latitude direction, unit: meter.

    .. py:attribute:: points_x
        :type: Union[list[int], tuple[int]]

        Number of the grid points along the longitude direction of each domain.

    .. py:attribute:: points_y
        :type: Union[list[int], tuple[int]]

        Number of the grid points along the latitude direction of each domain.

    .. py:attribute:: x_parent_index
        :type: Union[list[int], tuple[int]]

        Corresponding x index in the parent grid of the first point.

    .. py:attribute:: y_parent_index
        :type: Union[list[int], tuple[int]]

        Corresponding y index in the parent grid of the first point.

    .. py:attribute:: domain_num
        :type: int

        Domain number.

    .. py:attribute:: grid_spacing_ratio
        :type: Union[list[int], tuple[int]]

        Ratio of the grid resolution of each domain compared to the domain 1.

    .. py:attribute:: projection_type
        :type: Literal["lambert", "polar", "mercator", "lat-lon"]

        Projection type.

    .. py:attribute:: reference_lat
        :type: Union[int, float]

        Reference latitude.

    .. py:attribute:: reference_lon
        :type: Union[int, float]

        Reference longitude.

    .. py:attribute:: true_lat1
        :type: Union[int, float]

        True latitude (1:1 scale).

    .. py:attribute:: true_lat2
        :type: Union[int, float]

        True latitude (1:1 scale).

    .. py:attribute:: stand_lon
        :type: Union[int, float]

        Standard longitude.
    """

    # generally refers to the spacing of the parent grid points along the latitude, unit: meter
    resolution_x: int
    # spacing of the parent grid points along the longitude, unit: meter
    resolution_y: int
    # generally refers to the number of the grid points along the latitude.
    points_x: Union[list[int], tuple[int]]
    # number of the grid points along the longitude.
    points_y: Union[list[int], tuple[int]]
    # corresponding index in the parent grid of the first point.
    x_parent_index: Union[list[int], tuple[int]]
    y_parent_index: Union[list[int], tuple[int]]
    # domain number
    domain_num: int
    # ratio of the grid point spacing.
    grid_spacing_ratio: Union[list[int], tuple[int]]
    # projection type
    projection_type: Literal["lambert", "polar", "mercator", "lat-lon"]
    # reference point, true longitude and latitude
    reference_lat: Union[int, float]
    reference_lon: Union[int, float]
    true_lat1: Union[int, float]
    true_lat2: Union[int, float]
    stand_lon: Union[int, float]


__all__ = ["DomainSetting"]
