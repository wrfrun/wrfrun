``wrfrun.core`` Development Guide
##################################

:doc:`wrfrun.core </api/core>` provides the model-independent runtime for a simulation. It
creates one session for each :class:`~wrfrun.run.WRFRunContext`, gives model
plugins a place to register their executables and static workspace setup, and
keeps configuration, paths, commands, status, and replay data consistent for
that run.

Core must not contain model-specific filenames, namelist options, or binary
commands. Those belong to a model implementation and its plugin.

Core components
***************

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Component
     - Responsibility
   * - :class:`WRFRunSession <wrfrun.core.core.WRFRunSession>` and
       :data:`WRFRUN <wrfrun.core.core.WRFRUN>`
     - Hold and expose the services belonging to the active run.
   * - :class:`ConfigService <wrfrun.core.states.config.ConfigService>`
     - Load project and model TOML files, apply experiment overrides, create
       the run layout, and load enabled plugins.
   * - :class:`NamelistService <wrfrun.core.states.namelist.NamelistService>`
     - Store, update, and write namelists assembled by model executables.
   * - :class:`ResourceCatalog <wrfrun.core.runtime.resource.ResourceCatalog>`
       and :class:`RunLayout <wrfrun.core.runtime.resource.RunLayout>`
     - Describe resources with :class:`ResourceRef <wrfrun.core.type.ResourceRef>` and resolve paths for one run.
   * - :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>`
     - Define external-program input staging, execution, output collection,
       recording, and failure reporting.
   * - :class:`RunnerService <wrfrun.core.runtime.runner.RunnerService>` and
       :class:`IOService <wrfrun.core.runtime.io.IOService>`
     - Run argument-vector commands and perform shared file operations.
   * - :class:`ExecutableRegistry <wrfrun.core.runtime.registry.ExecutableRegistry>`
     - Keep executable classes registered by enabled model plugins for replay.
   * - :class:`WorkspaceService <wrfrun.core.runtime.workspace.WorkspaceService>`
     - Coordinate model-owned static workspace preparation and validation.
   * - :class:`ReplayService <wrfrun.core.runtime.record.ReplayService>` and
       :class:`RunStatusService <wrfrun.core.runtime.status.RunStatusService>`
     - Persist replay archives and the status consumed by job-management tools.

Session architecture
********************

:class:`WRFRunContext <wrfrun.run.WRFRunContext>` is the normal session boundary. On entry it creates a new
session, loads configuration, establishes project and run paths, and asks each
enabled model plugin to register its capabilities. Workspace validation and
initialization occur before executable calls. On exit, the context finishes the
run status and removes the session from the current context.

Within that boundary, model code accesses session-local services through
``WRFRUN``:

.. code-block:: python

   from wrfrun.core import WRFRUN

   model_config = WRFRUN.config.get_model_config("arps")
   output_dir = WRFRUN.resource.get_custom_resource(WRFRUN.resource.OUTPUT_DIR)
   WRFRUN.registry.register_exec("my_program", MyProgram)

Do not cache ``WRFRUN`` service objects, resolved paths, or plugin registrations
at module import time. They belong to the active session and can differ between
experiments and runs.

Configuration and plugins
*************************

Configuration loading follows this order:

1. Read the top-level project TOML file.
2. Expand enabled model TOML files.
3. Apply ``configs/experiments/<experiment>/experiment.toml`` when the active
   experiment is not ``common``.
4. Create the :class:`RunLayout <wrfrun.core.runtime.resource.RunLayout>` and
   register project, input, output, results, workspace, replay, temporary, and
   log resource providers.
5. Load each enabled model plugin and call its ``register()`` method.

Plugins are the extension boundary. A model plugin registers executable
classes, model workspace hooks, and any model-owned resource provider. It is
therefore the right place to connect a model to core; importing a model module
must not itself mutate a session registry.

Choosing where to change code
*****************************

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Requirement
     - Preferred location
   * - A binary needs different inputs, namelist preparation, or output rules
     - A model :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` subclass. See :doc:`Executable development <develop_guide_executable>`.
   * - A model needs installed binaries or immutable tables before a run
     - Its ``model/<name>/workspace.py`` and plugin workspace hooks.
   * - A model needs a new executable class or workspace provider
     - Its plugin ``register()`` method; do not add a global registry map.
   * - A feature is shared by more than one model
     - The smallest suitable core service, with session isolation and tests.
   * - A static packaged file is needed
     - :doc:`wrfrun/res </api/res>` and its resource declarations. See :doc:`resource development <develop_guide_res>`.
   * - Project creation, experiments, profiles, or job inspection changes
     - :doc:`wrfrun.core.operations </api/core.operations>` and the corresponding CLI command.

Adding or changing a core service
*********************************

Add a service only when it owns state or behavior shared across model
integrations. Keep model-specific policy outside core.

1. Put the service in :doc:`wrfrun.core.runtime </api/core.runtime>` when it operates during a run,
   or in :doc:`wrfrun.core.states </api/core.states>` when it represents loaded configuration,
   namelists, or mutable run state.
2. Add its constructor dependencies to the session assembly in
   :func:`create_wrfrun_session <wrfrun.core.core.create_wrfrun_session>`.
3. Expose it through :class:`WRFRunVarAPI <wrfrun.core.core.WRFRunVarAPI>` only
   when model integrations or other public core code need it.
4. Keep it independent of a concrete model package. Pass collaborators in
   rather than importing model code.
5. Add focused tests for a fresh session and for two independent sessions.
6. Update the relevant API docstring and this guide when its extension
   boundary changes.

Detailed guides
***************

- :doc:`Runtime services and session isolation <develop_guide_runtime>`
  explains service ownership, :class:`ResourceRef <wrfrun.core.type.ResourceRef>`, paths, workspace hooks, status,
  and replay.
- :doc:`Executable development <develop_guide_executable>` explains the
  :class:`ExecutableBase <wrfrun.core.base.ExecutableBase>` lifecycle, file handoffs, command execution, and replay
  configuration.
- :doc:`Model development <develop_guide_model>` describes the model plugin
  and project-file integration boundary.
- :doc:`Resource development <develop_guide_res>` describes packaged static
  files and generated resource constants.

Validation
**********

For core changes, run focused ``pytest`` tests first, then ``uv run ruff check
wrfrun tests`` and a Sphinx build when documentation changed. A successful unit
test does not prove an external model still runs: validate a representative
model workflow whenever the change affects session setup, resources, command
execution, workspace preparation, or output publication.
