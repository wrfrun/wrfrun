from wrfrun import WRFRUNConfig


def get_core_num() -> int:
    """
    Get core number.

    :return: Core number.
    :rtype: int
    """
    return WRFRUNConfig["core_num"]


__all__ = ["get_core_num"]
