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

Get started
***********

You can check the :doc:`usage/installation` and :doc:`usage/quick_start` page to install and explore ``wrfrun``.

.. toctree::
   :maxdepth: 3
   :caption: Get started:

   usage/installation
   usage/quick_start

User guide
**********

These sections will explain basic concepts of ``wrfrun``. You can also find the documentation of ``wrfrun``'s extensions here.

.. toctree::
   :maxdepth: 3
   :caption: User guide:

   documentation/config_file
   documentation/context
