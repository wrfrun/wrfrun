# Maintain `wrfrun` Documentation

Use this guide when changing or adding a user-visible feature, public API,
configuration key, command-line behavior, workspace layout, bundled resource,
or model workflow. Keep documentation consistent with the implementation and
make new capabilities discoverable from an appropriate index.

Treat source code, tests, and generated templates as the source of truth.
Do not document intended behavior that the current implementation does not
provide. State validation limits when runtime behavior was not exercised.

## Decide whether documentation changes are required

Update documentation when a change affects one or more of:

- Public classes, functions, parameters, return values, exceptions, or imports.
- User configuration, namelist behavior, templates, URI names, or defaults.
- Workspace structure, required executables, input staging, outputs, or replay.
- CLI commands, supported models, installation steps, or user workflows.
- A feature that users could not reasonably discover from the API reference.

Documentation-only changes are usually unnecessary for private refactoring with
no observable contract change. If a public docstring or existing guide becomes
incorrect, update it even when the code change is internal.

## Select the documentation surface

Use the smallest set that makes the feature discoverable:

- **API behavior**: update Sphinx-style docstrings and ensure the relevant
  `docs/source/api/*.rst` module page exists and is linked from its index.
- **How-to or workflow**: update or add a page under `docs/source/usage/`.
- **Concepts and configuration**: update `docs/source/documentation/`, such as
  the configuration or context guide.
- **Contributor-facing behavior**: update `docs/source/development/`.
- **Static configuration templates**: update the comments in `wrfrun/res/`
  together with the documentation page that explains the same user setting.
- **New model or executable**: document both the public API/wrapper and the
  user-visible inputs, outputs, prerequisites, and minimal invocation path.

Add a new page only when an existing page cannot describe the feature clearly.
Every new page must be reachable from the appropriate `index.rst` toctree;
do not leave guidance discoverable only through a direct path.

## Coordinate with implementation skills

Read the linked implementation skill before documenting its domain:

- For an `ExecutableBase` change, use `Executables.md`; document only the
  actual lifecycle, file handoff, replay, and output behavior.
- For workspace preparation or runtime static files, use `Workspace.md`;
  document the user-visible layout and prerequisites, not private helpers.
- For package resources or templates, use `Resources.md`; keep template
  comments, configuration documentation, and consumers synchronized.

Do not duplicate those skills' internal procedures in user documentation.

## Write accurate documentation

1. Inspect the changed implementation, public signatures, templates, and
   relevant tests before writing.
2. Preserve correct existing material; revise only what the new contract changes.
3. Use real names, paths, defaults, and examples from the code.
4. Distinguish confirmed runtime behavior from source-only analysis.
5. For a new workflow, include prerequisites, a minimal example, expected
   outputs, and a concise failure boundary when useful.
6. Link related API pages and guides rather than repeating long explanations.

Do not edit `docs/build/` or `docs/source/api/generated`; it is generated output.

## Validate documentation changes

1. Check every new or changed toctree entry and cross-reference target.
2. Confirm code snippets use current imports, arguments, paths, and config keys.
3. Build the Sphinx documentation when the environment provides the required
   dependencies, and fix actionable warnings.
4. If a full build is unavailable, run focused syntax/link checks where possible
   and state that the rendered build was not verified.
5. For documentation tied to a changed workflow, validate the implementation
   separately; documentation review does not prove runtime behavior.

## Finish the change

Summarize which documentation surfaces were updated and why. If no documentation
change was needed, state the checked public contract and the reason explicitly.