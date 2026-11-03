Developing ``wrfrun``
#####################

These pages are for contributors who change ``wrfrun`` itself: its session
runtime, model integrations, packaged resources, command-line operations, or
documentation. They complement the user guides, which explain how to create a
project and run an existing model.

Start here
**********

New contributors should read :doc:`the development environment guide
<environment>` first, then :doc:`the coding style <coding_style>`. The core
guide is the best next step before modifying behaviour shared by more than one
model.

Choose a guide by task
**********************

.. list-table::
   :widths: 67 33
   :header-rows: 1

   * - I need to...
     - Start with
   * - Set up the checkout, run checks, build docs, or build a distribution
     - :doc:`Development environment <environment>`
   * - Follow project conventions for scope, helpers, validation, docstrings,
       imports, or tests
     - :doc:`Coding style <coding_style>`
   * - Understand sessions, configuration loading, services, plugins, and
       where core changes belong
     - :doc:`Core architecture <develop_guide_core>`
   * - Add or modify a shared runtime service, paths, workspace hooks, command
       execution, status, or replay
     - :doc:`Runtime services <develop_guide_runtime>`
   * - Adapt an external program, its inputs, generated namelist, command, or
       archived outputs
     - :doc:`Executable development <develop_guide_executable>`
   * - Add support for a numerical model or change a model plugin
     - :doc:`Model development <develop_guide_model>`
   * - Add a packaged TOML template, scheduler script, or other static file
     - :doc:`Resource development <develop_guide_res>`

How the guides fit together
***************************

The :doc:`core guide <develop_guide_core>` describes the model-independent
session architecture. :doc:`Runtime services <develop_guide_runtime>` explain
the shared objects created for that session, while :doc:`executables
<develop_guide_executable>` define the model-specific lifecycle that consumes
them. A :doc:`model integration <develop_guide_model>` connects executable
classes, workspace hooks, and project directories through a plugin. Bundled
templates and scripts used by that integration are maintained through the
:doc:`resource guide <develop_guide_res>`.

For public classes, functions, and module-level details, use the
:doc:`API reference </api/index>`. When a change affects user workflows,
configuration, or command-line behaviour, also update the relevant user-facing
page under :doc:`the documentation section </documentation/index>` or
:doc:`the usage section </usage/index>`.

Development pages
*****************

.. toctree::
   :maxdepth: 1
   :caption: Development

   environment
   coding_style
   wrfrun_develop_guide
