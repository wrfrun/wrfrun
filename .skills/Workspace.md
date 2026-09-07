# Manage `wrfrun` Workspaces

Use this guide when adding a model, changing its runtime directory layout, or changing the static files required before an executable runs. Treat `wrfrun/core/runtime/workspace.py`, the relevant module in `wrfrun/model/<model>/workspace.py`, and the model plugin as the source of truth.

## Preserve the workspace layout

``ConfigService`` registers the project, input, output, workspace, temporary,
replay, log, and template providers for the active session. Each model plugin
may add a model workspace provider beneath ``WRFRUN_NEW.resource.WORKSPACE_DIR``.
Use provider-relative paths rather than prescribing a global filesystem layout.

## Define workspace paths through resource providers

Build model workspace paths with ``ResourceRef``. Register the model provider
from its plugin, then resolve it with ``WRFRUN_NEW.resource`` only where a real
``Path`` is required.

For a model plugin:

1. Register executable classes with ``WRFRUN_NEW.registry``.
2. Register workspace init/check functions with ``WRFRUN_NEW.workspace``.
3. Register a model workspace provider with ``WRFRUN_NEW.resource``.

Registration is session-local and happens after the enabled model plugin is
loaded. Do not use old URI hooks or module-import registration for new code.

## Prepare only model-owned runtime resources

Implement ``prepare_<model>_workspace()`` in
``wrfrun/model/<model>/workspace.py`` to:

1. Validate the model installation directory and required executable files before modifying the workspace.
2. Create or refresh only the workspace directories owned by that model.
3. Stage static runtime resources: executables, immutable tables, and files required before execution.
4. Log failures with the missing path or resource name.

Do not modify the model installation directory. Do not populate project
``templates/`` or ``namelists/`` during workspace initialization; those files
must be ready before a simulation starts. Do not pre-stage temporary inputs or
result files that an `Executable` creates or collects during its lifecycle.

Choose the staging method from the program's behavior:

- Link read-only installed resources when the program can safely use them in place.
- Copy files that the program modifies, renames, or requires to be independent.
- Specify destination names and directories explicitly when the runtime contract requires them.

## Limit destructive cleanup

`check_path(..., force=True)` recursively removes an existing directory before recreating it. Use it only for a model workspace that the prepare function exclusively owns. Never apply it to an installation, input-data directory, output archive, or shared workspace.

`prepare_workspace()` backs up an existing main workspace while reinitializing and attempts to restore it on failure. This does not remove the need for narrow cleanup: validate configuration and installed resources before replacing model directories, and expect a first-time failed preparation to leave partial workspace content.

## Register preparation and validation

Register ``prepare_<model>_workspace`` and ``check_<model>_workspace`` from
the model plugin with ``WRFRUN_NEW.workspace.register_init_func`` and
``register_check_func``. A model workspace function reads the enabled model
configuration from ``WRFRUN_NEW.config``.

``WRFRunContext.__enter__`` checks registered workspaces before entering the
execution context and initializes them when requested or invalid. Keep prepare
functions repeatable and dependent only on the active session.

## Coordinate with Executables

When adding or changing an `ExecutableBase` subclass, review its `work_path` and all static runtime prerequisites. Update the relevant workspace module when the executable needs a new component directory, executable binary, immutable table, or other file that must exist before `before_exec` runs.

Keep the boundary explicit: workspace preparation owns static installation-derived resources; the executable owns generated configuration, run-specific input staging, execution, and output collection. See [Executables.md](Executables.md) for the executable lifecycle.

## Synchronize documentation

When a workspace change affects a public path, required installation resource, setup procedure, supported model component, or user workflow, read [Documentation.md](Documentation.md). Document the visible contract without duplicating private workspace implementation details.

## Validate the change

Before handing off a workspace change:

1. In an active session, verify each ``ResourceRef`` resolves to the expected path.
2. Verify invalid installation paths and missing required programs fail before destructive workspace changes.
3. Verify preparation creates only the model-owned directories and places every required link or copy at its intended destination.
4. Verify model-specific checking detects a missing critical directory or resource; state the gap if no check function exists.
5. Run ``WRFRunContext(..., init_workspace=True)`` and verify that the dependent executable can start from its designated workspace.
