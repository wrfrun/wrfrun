Model Development Guide
#######################

Adding a model means connecting its executables and project conventions to the
model-independent core runtime. A complete integration lets a user create a
project, enable the model, prepare an isolated workspace, run its executables,
and archive outputs without model-specific logic leaking into
:doc:`wrfrun.core </api/core>`.

This guide describes the complete route for a new model named ``my_model``.
Inspect an existing model with similar requirements before choosing filenames,
namelist handling, or workspace staging rules.

What a model integration contains
*********************************

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Part
     - Purpose
   * - Model package
     - Public wrappers and model-specific implementation modules under
       ``wrfrun/model/my_model/``.
   * - Plugin
     - Registers executable classes, workspace hooks, resource providers, and
       model-owned project directories.
   * - Executables
     - Adapt each external program through
       :class:`wrfrun.core.base.ExecutableBase`.
   * - Workspace hooks
     - Stage static installation-derived binaries and immutable tables when
       the model needs them before an executable runs.
   * - Namelist or parameter handling
     - Read a model's project templates and updates, derive required values,
       and write final files in the executable workspace.
   * - Configuration template
     - Supply model TOML defaults and make project creation able to copy them.
   * - Build and discovery wiring
     - Install Python and static resources, and make the plugin and model
       template discoverable to the CLI and configuration loader.

Step 1: Define the model contract
*********************************

Before creating files, identify the external programs and their handoffs:

1. List each executable, its binary name, its static installed prerequisites,
   and its working directory.
2. List the required inputs, including which inputs come from project data and
   which come from another executable result.
3. List generated configuration files, their base template, and user or
   experiment update files.
4. List outputs, logs, and the output patterns that should be archived.
5. Decide which constructor arguments and generated settings are needed for
   replay.

This contract determines whether the model needs several executable classes,
separate namelist components, and workspace hooks. Do not create generic
abstractions before the model has a concrete requirement for them.

Step 2: Create the model package
********************************

Create a package under ``wrfrun/model/my_model/``. A typical layout is::

   wrfrun/model/my_model/
       __init__.py       # Explicit public wrappers and classes.
       plugin.py         # MyModelPlugin.
       core.py           # ExecutableBase subclasses.
       exec_wrap.py      # Optional thin user-facing wrappers.
       namelist.py       # Optional model-specific namelist preparation.
       workspace.py      # Optional static workspace hooks.
       meson.build       # Installation wiring for package modules.

Split executable implementations into separate modules when that makes their
inputs and namelist logic clearer. Keep ``__init__.py`` limited to the model's
intended public API, using explicit imports and ``__all__``.

.. important::

   Do not import ``my_model`` from :doc:`wrfrun.model </api/model>`. Model
   packages are deliberately loaded through their plugins only when
   configuration enables them. Eager imports slow package startup and can
   register resources outside an active session.

Step 3: Implement the plugin
****************************

The plugin is the integration point between the model and an active session.
It implements :class:`wrfrun.core.plugin.PluginProtocol` and is loaded through
:doc:`wrfrun.model.plugins </api/model.plugins>` and its ``PLUGIN_MAP``.

.. code-block:: python

   from pathlib import Path

   from wrfrun.core import WRFRUN

   from .core import MyProgram
   from .workspace import check_my_model_workspace, prepare_my_model_workspace


   class MyModelPlugin:
       name = "my_model"

       def initialize_project_files(self, project_path: Path):
           (project_path / "configs/namelists/templates/my_model/my_program").mkdir(
               parents=True,
               exist_ok=True,
           )
           (project_path / "configs/namelists/user/my_model/my_program").mkdir(
               parents=True,
               exist_ok=True,
           )

       def initialize_experiment_files(self, experiment_path: Path):
           (experiment_path / "namelists/my_model/my_program").mkdir(
               parents=True,
               exist_ok=True,
           )

       def register(self):
           WRFRUN.registry.register_exec("my_program", MyProgram)
           WRFRUN.workspace.register_init_func("my_model", prepare_my_model_workspace)
           WRFRUN.workspace.register_check_func("my_model", check_my_model_workspace)
           WRFRUN.resource.register_provider(
               "workspace_my_model",
               WRFRUN.resource.WORKSPACE_DIR / "my_model",
           )

Implement :meth:`~wrfrun.core.plugin.PluginProtocol.initialize_project_files`
and :meth:`~wrfrun.core.plugin.PluginProtocol.initialize_experiment_files`
even when the model has no namelist directories; an empty method makes that
ownership explicit. Register only workspace hooks that the model actually
implements.

.. important::

   :meth:`~wrfrun.core.plugin.PluginProtocol.register` runs once in an active
   session after configuration has been loaded. Do not register executable
   classes, providers, or hooks when ``plugin.py`` is imported. Replay and
   separate experiments rely on this registration being session-local.

Step 4: Add static workspace preparation when needed
*****************************************************

Implement ``prepare_my_model_workspace`` and ``check_my_model_workspace`` in
``workspace.py`` only for resources that must exist before an executable
starts: installed binaries, immutable lookup tables, or a fixed directory
structure. Link read-only files when the model can use them in place; copy a
file only when the program modifies it.

Generated namelists, run-specific data, and executable outputs do not belong
in workspace preparation. They belong in the executable lifecycle.

See :doc:`runtime services <develop_guide_runtime>` for the session and
provider boundary.

Step 5: Implement executables and wrappers
*******************************************

Create one :class:`wrfrun.core.base.ExecutableBase` subclass for each external
program with a distinct input, command, or output contract. Give it a stable
name, a provider-relative workspace :class:`wrfrun.core.type.ResourceRef`, and
an argument-vector command. In
:meth:`~wrfrun.core.base.ExecutableBase.before_exec`, register inputs and write
generated configuration; in :meth:`~wrfrun.core.base.ExecutableBase.after_exec`,
register output patterns before calling the parent method.

When the model benefits from a concise public interface, expose a thin wrapper
that constructs and invokes the executable. Keep staging, namelist preparation,
and output collection in the executable class rather than the wrapper.

See :doc:`executable development <develop_guide_executable>` for the lifecycle,
recording, replay, failure artifacts, and handoff rules.

Step 6: Define namelist and project-file ownership
***************************************************

For a model that uses namelists, its plugin creates the directories it owns:

1. ``configs/namelists/templates/<model>/<component>/`` for base files.
2. ``configs/namelists/user/<model>/<component>/`` for project-wide updates.
3. ``configs/experiments/<experiment>/namelists/<model>/<component>/`` for
   experiment-specific updates.

The executable reads its template, applies values derived from model TOML,
then applies user and experiment updates before writing the final namelist in
its workspace. Choose one component name per independently prepared namelist;
do not make unrelated executables share an identifier merely because their
current files happen to be similar.

.. important::

   Project initialization creates directories, not a hidden copy of a model's
   installation namelist. A user-controlled base template must be available
   before a simulation starts.

Step 7: Add configuration and discovery wiring
************************************************

A new model must be discoverable in all of these places:

1. Add ``wrfrun/res/config/my_model.template.toml`` with the concise model
   settings that executables actually consume.
2. Add it to ``wrfrun/res/config/name_map.json`` and
   ``wrfrun/res/config/meson.build``, then regenerate ``wrfrun/res/__init__.py``.
3. Add the model's ``use`` and ``include`` entry to
   ``wrfrun/res/config/config.template.toml``.
4. Add the generated template constant to ``MODEL_MAP`` in
   :doc:`wrfrun.core.operations.project </api/core.operations.project>` so
   project initialization and ``wrfrun model add`` can copy it.
5. Add ``"my_model": "wrfrun.model.my_model.plugin:MyModelPlugin"`` to
   ``PLUGIN_MAP`` in :doc:`wrfrun.model.plugins </api/model.plugins>`.
6. Add the package subdirectory to ``wrfrun/model/meson.build`` and create its
   own ``meson.build`` so every Python module is installed.

See :doc:`resource development <develop_guide_res>` for generated constants,
resource declarations, and installed-package validation.

Step 8: Test the complete path
******************************

Test more than a direct import. A complete model integration should verify:

1. ``wrfrun init --models my_model`` creates the TOML file, input directory,
   and plugin-owned namelist directories.
2. Creating an experiment creates model-owned experiment namelist directories
   and stages the experiment input tree.
3. Loading a configuration imports the plugin only when ``use = true`` and
   registers all intended executable classes.
4. Workspace preparation stages every required static resource without
   modifying the model installation.
5. A representative executable stages inputs, writes its final namelist, runs,
   archives outputs and logs, and publishes its latest result.
6. Record and replay work for every executable with custom constructor or
   namelist state.

Run focused ``pytest`` tests, ``uv run ruff check wrfrun tests``, and a Sphinx
build after changing developer documentation. Run a real model smoke test when
the required installation and input data are available.

Further reading
***************

- :doc:`Core architecture <develop_guide_core>` explains session and plugin
  loading boundaries.
- :doc:`Runtime services <develop_guide_runtime>` explains resources and
  workspace hooks.
- :doc:`Executable development <develop_guide_executable>` covers execution
  lifecycle and replay details.
- :doc:`Resource development <develop_guide_res>` covers packaged TOML
  templates and Meson installation wiring.
