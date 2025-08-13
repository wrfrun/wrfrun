"""
wrfrun.extension
################

Through extensions, developers can add more functionality to ``wrfrun``.
``wrfrun`` now has the following extensions:

========================================= ==========================================
:doc:`goos_sst </api/extension.goos_sst>` Process NEAR-GOOS SST data.
:doc:`littler </api/extension.littler>`   Process LITTLE_R observation data.
========================================= ==========================================

Other Submodules
****************

=================================== ==========================================
:doc:`utils </api/extension.utils>` Utility methods can be used by extensions.
=================================== ==========================================

.. toctree::
    :maxdepth: 1
    :hidden:

    goos_sst <extension.goos_sst>
    littler <extension.littler>
    utils <extension.utils>
"""

from .utils import *
