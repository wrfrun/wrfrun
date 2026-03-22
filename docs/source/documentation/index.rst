Documentation
#############

Welcome to the ``wrfrun`` documentation! This section provides in-depth explanations of ``wrfrun``'s core concepts, architecture, and internal mechanisms. 
While the :doc:`/usage/index` section focuses on *how to use* ``wrfrun``, this section focuses on *how it works* under the hood.

Whether you're looking to understand the framework better, troubleshoot issues, or extend ``wrfrun`` with your own functionality, this documentation will give you the insights you need.

.. toctree::
   :maxdepth: 2
   :caption: Documentation
   :hidden:

   config_file
   context
   global_var_wrfrun

Core Concepts
*************

Configuration File
==================

The :doc:`config_file` guide explains everything you need to know about ``wrfrun``'s TOML-based configuration system:

- The structure of the main configuration file and model-specific configuration files
- All available configuration options and what they control
- How to reference and include other configuration files
- How the configuration is loaded and merged
- Best practices for organizing your configuration files

This is essential reading for understanding how to customize ``wrfrun`` for your specific needs.

WRFRun Context Manager
======================

The :doc:`context` document dives deep into the :class:`WRFRun <wrfrun.run.WRFRun>` context manager, which is the heart of every ``wrfrun`` simulation:

- How the context manager works internally
- What happens during the ``__enter__`` and ``__exit__`` phases
- The different initialization options and their effects
- How job submission, server startup, and data preparation are handled
- Best practices for using the context manager effectively

Understanding this will help you use :class:`WRFRun <wrfrun.run.WRFRun>` more effectively and troubleshoot any issues that may arise.

Global Variable ``WRFRUN``
===========================

The :doc:`global_var_wrfrun` page explains the global :py:data:`WRFRUN <wrfrun.core.core.WRFRUN>` singleton proxy:

- What :py:data:`WRFRUN <wrfrun.core.core.WRFRUN>` is and why it exists
- The three core components it manages: configuration, executable database, and simulation recorder
- How to use each of these components
- The initialization lifecycle of the global variable
- Callback mechanisms for extension development

This is particularly important if you're interested in developing extensions to ``wrfrun``.

``WRFRUN.config`` Property
++++++++++++++++++++++++++

The :doc:`global_var_wrfrun_config` document provides a comprehensive look at the :class:`WRFRunConfig <wrfrun.core._config.WRFRunConfig>` class:

- The mixin architecture and what each mixin provides
- Detailed explanations of :class:`ConstantMixIn <wrfrun.core._constant.ConstantMixIn>`, :class:`ResourceMixIn <wrfrun.core._resource.ResourceMixIn>`, :class:`NamelistMixIn <wrfrun.core._namelist.NamelistMixIn>`, and :class:`DebugMixIn <wrfrun.core._debug.DebugMixIn>`
- How to work with resource URIs for cross-environment compatibility
- Namelist management for numerical models
- Debug mode configuration and usage
- Complete API reference for all configuration-related functionality

This is the most technical document in this section and is particularly valuable for developers working on ``wrfrun`` itself.

Where to Go Next
*****************

After exploring these core concepts, you may want to:

- Check the :doc:`/api/index` for complete API documentation
- Look at the :doc:`/development/index` section if you're interested in contributing to ``wrfrun``
- Review the :doc:`/usage/index` section for practical usage examples

If you have questions about any of these concepts, don't hesitate to open an issue on the `GitHub repository <https://github.com/wrfrun/wrfrun/issues>`_.
