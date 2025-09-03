"""
wrfrun.extension.littler
########################

This extension can help you manage observation data, and create ``LITTLE_R`` file for data assimilation.

========================================= =============================
:doc:`core </api/extension.littler.core>` Core functionality submodule.
========================================= =============================

What Can This Extension Do?
***************************

According to the `WRFDA Online Tutorial <https://www2.mmm.ucar.edu/wrf/users/wrfda/OnlineTutorial/Help/littler.html>`_,
``LITTLE_R`` is an ASCII-based observation file format that is designed to be an intermediate format
so that WRFDA might be able to assimilate as many observation types as possible in a universal manner.

However, ``LITTLE_R`` is really hard to process elegantly from the point of view of Python.
To help users create ``LITTLE_R`` file easily, this extension introduces :class:`LittleR <core.LittleR>`,
and **Zipped Little R** file.

:class:`LittleR <core.LittleR>` accepts observation datas, and can generate observation reports in proper format.
Besides, it can save an observation report to a Zipped Little R file,
so you can read the report later or process the observation data with other program.
Please check :class:`LittleR <core.LittleR>` for more information.

How To Use This Extension?
**************************

The code snap below shows you how to use this extension.

.. code-block:: Python
    :caption: main.py
    
    from wrfrun.extension.littler import LittleR


    if __name__ == '__main__':
        littler = LittleR()
        littler.set_header(
            longitude=120, latitude=60, fm="FM-19", elevation=0,
            is_bogus=True, date="20250902070000"
        )
        # write to LITTLE_R file
        with open("data/test", "w") as f:
            f.write(str(littler))
        # write to zlr file
        littler.to_zlr("data/test.zlr")

.. toctree::
    :maxdepth: 1
    :hidden:

    core <extension.littler.core>
"""

from .core import *
