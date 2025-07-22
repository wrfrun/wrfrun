.. wrfrun documentation master file, created by
   sphinx-quickstart on Sun Feb 16 12:49:45 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

wrfrun documentation
####################

.. note::
   I'm still working on to complete ``wrfrun``'s documentation, you'll find some empty pages, which is normal :)

   I hope you like my work.

What is wrfrun?
***************

``wrfrun`` is a comprehensive toolkit for managing and using WRF. ``wrfrun`` wraps the WRF model so that the user only needs to call the corresponding Python function to run the corresponding part of the model. ``wrfrun`` avoids cluttering up the user's working directory with a lot of useless files by creating a temporary directory in which the WRF model would be run. ``wrfrun`` automatically saves mode configurations and wrfrun configurations, which makes it easier to manage the simulation and reproduction of different cases. ``wrfrun`` also provides more features through extensions, which help users to do related research better.

Main features
*************

* Provide Python functions with the same names as WRF executables.
* Isolate the entire simulation in a temporary directory, avoid messing up your project directory.
* Automatically save all configurations (including ``wrfrun`` config file and namelist files) after completing simulation.
* Record your simulation progress, export simulation configurations and data to a ``.replay`` file.
* Replay simulations based on your provided ``.replay`` file.

Get started
***********

These sections will teach you how to install ``wrfrun``, and help you explore ``wrfrun`` using the same cases from `WRF–ARW Online Tutorial <https://www2.mmm.ucar.edu/wrf/OnLineTutorial/>`_.

.. toctree::
   :maxdepth: 3
   :caption: Get started:

   usage/index

User guide
**********

These sections will explain important concepts of ``wrfrun`` and help you understand how ``wrfrun`` works.

.. toctree::
   :maxdepth: 3
   :caption: User guide:

   documentation/index

API reference
*************

:doc:`/api/index` contains a detailed description of the ``wrfrun`` API. It describes how the methods work and which parameters can be used.

.. toctree:: 
   :hidden:
   :maxdepth: 2

   api/index
