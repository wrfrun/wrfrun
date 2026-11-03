"""
wrfrun.model
############

Model integrations and shared utilities.

Model packages are loaded through their plugins when a project enables the
corresponding model; importing this package does not import ARPS, PALM, ROMS,
or WRF implementations.

Submodules
**********

========================================= ========================================================
:doc:`arps </api/model.arps>`             ARPS model integration.
:doc:`constants </api/model.constants>`   Shared model constants.
:doc:`namelist </api/model.namelist>`     Project namelist-file discovery.
:doc:`palm </api/model.palm>`             PALM model integration.
:doc:`plot </api/model.plot>`             Domain plotting utilities.
:doc:`plugins </api/model.plugins>`       Model-plugin loading.
:doc:`roms </api/model.roms>`             ROMS model integration.
:doc:`type </api/model.type>`             Shared model types.
:doc:`utils </api/model.utils>`           Shared model utilities.
:doc:`wrf </api/model.wrf>`               WRF and WPS model integration.
========================================= ========================================================

.. toctree::
    :maxdepth: 1
    :hidden:

    arps <model.arps>
    constants <model.constants>
    namelist <model.namelist>
    palm <model.palm>
    plot <model.plot>
    plugins <model.plugins>
    roms <model.roms>
    type <model.type>
    utils <model.utils>
    wrf <model.wrf>
"""

from .constants import NamelistName
from .plot import create_projection, generate_domain_area, plot_domain_area
from .plugins import load_model_plugin
from .type import DomainSetting
from .utils import clear_model_logs

__all__ = [
    "DomainSetting",
    "NamelistName",
    "clear_model_logs",
    "create_projection",
    "generate_domain_area",
    "load_model_plugin",
    "plot_domain_area",
]
