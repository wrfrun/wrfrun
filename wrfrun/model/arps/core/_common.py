"""Shared ARPS executable helpers."""

from wrfrun.core import WRFRUN_NEW

from ..namelist import prepare_arps_namelist


def check_and_prepare_arps_namelist() -> None:
    """Load the project ARPS namelist when it is not already available."""
    if not WRFRUN_NEW.namelist.check_namelist("arps"):
        prepare_arps_namelist()


__all__ = ["check_and_prepare_arps_namelist"]
