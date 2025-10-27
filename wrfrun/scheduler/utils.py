from wrfrun.core import get_wrfrun_config


def get_core_num() -> int:
    """
    Get core number.

    :return: Core number.
    :rtype: int
    """
    return get_wrfrun_config()["core_num"]


__all__ = ["get_core_num"]
