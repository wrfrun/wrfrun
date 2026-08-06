# Manage `wrfrun` Workspaces

Use this guide when adding a model, changing its runtime directory layout, or changing the static files required before an executable runs. Treat `wrfrun/core/uri.py`, `wrfrun/workspace/core.py`, and the relevant module in `wrfrun/workspace/` as the source of truth.

## Preserve the workspace layout

Treat the configured work root as a collection of framework and model directories:

- `<work-root>/tmp`: framework temporary files.
- `<work-root>/workspace/replay`: replay working files.
- `<work-root>/workspace/model`: root for model workspaces.

Allow each model to define the subdirectories its runtime requires. For example, WRF has WPS, WRF, and WRFDA directories, while ARPS, PALM, and ROMS each use a model root. Do not generalize one model's directory names or depth to another model.

## Define workspace paths through URIs

Build model workspace paths from `WRFRUN.uri.WRFRUN_WORKSPACE_MODEL`; do not hard-code host filesystem paths.

For each model module:

1. Define module-level workspace URI variables with empty-string defaults.
2. Define a URI hook that sets those variables from the URI manager.
3. Register the hook with `WRFRUN.set_uri_register_func(...)` at module import time.
4. Provide a public path getter with an interface appropriate to the model.

Do not use a workspace variable before the URI manager has initialized and invoked its hook. Before calling filesystem APIs such as `exists`, `listdir`, directory creation, copying, or linking, resolve the URI with `WRFRUN.uri.parse_resource_uri(...)`.

`WORKSPACE_MODEL_<component>` is a useful existing pattern, not a required name. Use a stable, descriptive name and make the getter the public interface consumed by model executables.

## Prepare only model-owned runtime resources

Implement `prepare_<model>_workspace(model_config)` in `wrfrun/workspace/<model>.py` to:

1. Validate the model installation directory and required executable files before modifying the workspace.
2. Create or refresh only the workspace directories owned by that model.
3. Stage static runtime resources: executables, immutable tables, and files required before execution.
4. Log failures with the missing path or resource name.

Do not modify the model installation directory. Do not pre-stage namelists, temporary inputs, or result files that an `Executable` creates or collects during its lifecycle.

Choose the staging method from the program's behavior:

- Link read-only installed resources when the program can safely use them in place.
- Copy files that the program modifies, renames, or requires to be independent.
- Specify destination names and directories explicitly when the runtime contract requires them.

## Limit destructive cleanup

`check_path(..., force=True)` recursively removes an existing directory before recreating it. Use it only for a model workspace that the prepare function exclusively owns. Never apply it to an installation, input-data directory, output archive, or shared workspace.

`prepare_workspace()` backs up an existing main workspace while reinitializing and attempts to restore it on failure. This does not remove the need for narrow cleanup: validate configuration and installed resources before replacing model directories, and expect a first-time failed preparation to leave partial workspace content.

## Register preparation and validation

Import each model's prepare function in `wrfrun/workspace/core.py` and add it to `PREPARE_FUNC_MAP`. Without this registration, `prepare_workspace()` skips the model and reports that its workspace may be incomplete.

Implement and register `check_<model>_workspace(model_config)` in `CHECK_FUNC_MAP` when possible. A missing check function causes `check_workspace()` to skip model-specific validation; for a model with binaries, tables, or multiple directories, checking only that its root exists is usually insufficient. `register_workspace_func(...)` is also available where dynamic registration is appropriate.

`WRFRun.__enter__` checks the workspace before entering the execution context. It calls preparation when validation fails or when the caller requests `init_workspace=True`. Keep prepare functions repeatable and dependent only on initialized `WRFRUN` URI and configuration state.

## Coordinate with Executables

When adding or changing an `ExecutableBase` subclass, review its `work_path` and all static runtime prerequisites. Update the relevant workspace module when the executable needs a new component directory, executable binary, immutable table, or other file that must exist before `before_exec` runs.

Keep the boundary explicit: workspace preparation owns static installation-derived resources; the executable owns generated configuration, run-specific input staging, execution, and output collection. See [Executables.md](Executables.md) for the executable lifecycle.

## Validate the change

Before handing off a workspace change:

1. Initialize the URI manager and verify each public getter returns the expected URI and resolved path.
2. Verify invalid installation paths and missing required programs fail before destructive workspace changes.
3. Verify preparation creates only the model-owned directories and places every required link or copy at its intended destination.
4. Verify model-specific checking detects a missing critical directory or resource; state the gap if no check function exists.
5. Run `WRFRun(..., init_workspace=True)` and verify that the dependent executable can start from its designated workspace.
