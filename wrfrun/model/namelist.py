"""
wrfrun.model.namelist
#####################

Shared paths for project namelist files.

.. autosummary::
    :toctree: generated/

    get_project_namelist_files
"""

from pathlib import Path

from ..core import WRFRUN_NEW


def get_project_namelist_files(model: str, component: str, filename: str) -> tuple[Path, tuple[Path, ...]]:
    """Return the template and optional update files for one namelist."""
    resource = WRFRUN_NEW.resource
    template = resource.get_custom_resource(resource.NAMELIST_TEMPLATE_DIR / model / component / filename)
    updates = [resource.get_custom_resource(resource.NAMELIST_USER_DIR / model / component / filename)]

    if resource.layout.experiment != "common":
        updates.append(
            resource.get_custom_resource(
                resource.CONFIG_DIR / f"experiments/{resource.layout.experiment}/namelists/{model}/{component}/{filename}"
            )
        )

    return template, tuple(updates)


__all__ = ["get_project_namelist_files"]
