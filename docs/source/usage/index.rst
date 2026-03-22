Usage
#####

Welcome to the ``wrfrun`` usage guide! This section will help you get started with ``wrfrun`` and learn how to use its various features effectively.

Whether you're new to ``wrfrun`` or an experienced user looking to explore advanced features, this guide has you covered. 
The documentation is organized to take you from basic installation through to advanced customization.

.. toctree::
   :maxdepth: 2
   :caption: Usage
   :hidden:

   installation
   quick_start
   custom_executable

Getting Started
***************

Installation
============

The first step to using ``wrfrun`` is installing it on your system. The :doc:`installation` guide provides detailed instructions for different installation methods, including:

- Installing from PyPI using pip or uv
- Installing from source for development
- Optional dependencies for additional features
- Verifying your installation

Start here if you haven't installed ``wrfrun`` yet!

Quick Start
===========

Once you have ``wrfrun`` installed, the :doc:`quick_start` guide is the perfect place to learn the basics. 
This hands-on tutorial walks you through a complete WRF simulation of Hurricane Matthew, teaching you:

- How to prepare your configuration file
- How to set up your simulation domain
- Running WPS programs (geogrid, ungrib, metgrid)
- Running WRF initialization and simulation
- Using job schedulers for cluster computing
- Recording and replaying simulations for reproducibility

This tutorial is designed to be followed step-by-step, even if you're new to WRF modeling.

Advanced Usage
**************

Define custom ``Executable``
============================

Ready to extend ``wrfrun`` or integrate custom programs? 
The :doc:`custom_executable` tutorial teaches you how to create your own ``Executable`` classes, which is the foundation for:

- Integrating new model components
- Adding custom preprocessing or postprocessing steps
- Creating reusable simulation components
- Understanding how ``wrfrun`` manages external programs

This guide covers everything from basic ``Executable`` creation to advanced features like MPI support and the record/replay system.

Where to Go Next
*****************

After exploring the usage guides, you may want to check out:

- :doc:`/documentation/index`: In-depth explanations of ``wrfrun`` concepts and architecture
- :doc:`/api/index`: Complete API reference for all ``wrfrun`` modules
- :doc:`/development/index`: For those interested in contributing to ``wrfrun`` development

If you have questions or run into issues, don't hesitate to check the project's `GitHub issues <https://github.com/wrfrun/wrfrun/issues>`_ page.
