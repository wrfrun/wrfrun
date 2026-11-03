``wrfrun`` Coding Style
#######################

This page describes the conventions for code maintained in ``wrfrun``. The
main goal is direct, readable code whose structure reflects the current runtime
contract. Prefer a small complete implementation to an abstraction for a
possible future use case.

Quick Checks
************

The project uses `Ruff <https://docs.astral.sh/ruff/>`_ for formatting,
linting, and import ordering. Run checks through the project's ``uv``
environment:

.. code-block:: bash

    uv run ruff format --check wrfrun tests
    uv run ruff check wrfrun tests
    uv run pyright
    uv run pytest

Use ``uv run ruff format wrfrun tests`` and ``uv run ruff check --fix
wrfrun tests`` when an automatic correction is appropriate. ``pyproject.toml``
sets the Python version to 3.10 and the Ruff line length to 130 characters.
Run the narrowest relevant test first; run the complete test suite when a
change affects shared core behaviour.

Implementation Principles
*************************

- Prefer the simplest implementation that satisfies a present, observable
  requirement. Generalize only when a concrete second use case requires it.
- Keep a short operation at its call site. Introduce a helper only when it
  expresses a domain concept or removes substantial repeated logic.
- Do not duplicate validation that an immediate I/O operation or framework
  boundary already performs. Add a preflight check only when it changes the
  error meaningfully, prevents an unsafe mutation, or enforces a boundary the
  lower layer cannot enforce.
- Make failure messages actionable, especially at external-command and file
  boundaries. Do not hide a useful underlying exception with a vague wrapper.
- Optimize measured bottlenecks, not anticipated ones. Leave a concise
  comment when an otherwise surprising implementation is necessary for
  performance or compatibility.

Formatting and Names
********************

Use four spaces for indentation, double quotes for ordinary strings, and
trailing commas in multi-line literals and signatures. Let Ruff handle import
ordering and most mechanical formatting.

Follow normal Python naming:

- Classes use ``PascalCase``.
- Functions, methods, variables, and modules use ``snake_case``.
- Module constants use ``UPPER_SNAKE_CASE``.
- Private implementation details begin with one underscore.

Use names from the simulation domain when they make the data flow clearer:
``history_source`` is preferable to a generic ``source`` when it denotes the
origin of ARPS history files. Avoid abbreviations that are not established by
the model or its namelist.

Types and Imports
*****************

Type public APIs, configuration structures, and values that cross service or
model boundaries. Use Python 3.10 union syntax such as ``Path | None`` and
``TypedDict`` or a dataclass when a mapping has a stable shape. A local type
annotation is useful when it clarifies a non-obvious value; it is not required
for every straightforward expression.

Group imports into standard-library, third-party, and local imports, separated
by blank lines. Prefer explicit imports and declare the deliberately public
surface of a package with ``__all__``. Do not use ``from module import *``,
including in ``__init__.py`` files.

A top-level model package must not eagerly import every model implementation.
Model support is loaded through its plugin only when the corresponding model is
enabled. This keeps ``import wrfrun`` lightweight and prevents optional model
requirements from becoming unconditional dependencies.

Runtime Boundaries
******************

The current runtime is session-local. Access its services through
:class:`wrfrun.core.core.WRFRunVarAPI` only while a
:class:`wrfrun.run.WRFRunContext` is active; :data:`wrfrun.core.core.WRFRUN`
is a context-local port, not a process-wide store for mutable run state.

Represent locations managed by the runtime with
:class:`wrfrun.core.type.ResourceRef`. Resolve a reference through the active
resource service immediately before an operation requires a real
:class:`pathlib.Path`. This preserves portable configuration while keeping
filesystem operations explicit.

Plugins register executable classes and model resources in the active session.
Do not register them as an import side effect or in a module-level mutable
registry. See :doc:`the core guide <develop_guide_core>` and
:doc:`the model guide <develop_guide_model>` for the surrounding architecture.

Comments and Docstrings
************************

Write comments for intent, constraints, or non-obvious decisions—not to repeat
the code directly below them. Keep them close to the code they explain and
remove them when the code changes.

Docstrings should let a user or contributor understand what a public module,
class, or function provides, why it is useful, and how to use it. Start with a
short direct description. Add only the detail needed to use the API correctly;
internal implementation narration and redundant ``:param:``/``:type:`` fields
are usually noise when annotations and names already convey that information.
A short doctest is encouraged when it demonstrates the normal usage or fixes a
subtle contract.

Python module docstrings are also Sphinx source material:

- A concrete module begins with its full module path as an RST heading and an
  ``autosummary`` list of its public classes and functions.
- A package ``__init__.py`` gives a short overview, a table of its direct
  submodules, and a hidden ``toctree``. It does not use ``autosummary``.
- Every documented module has an API page under ``docs/source/api`` named for
  its full package hierarchy.

Follow :doc:`the core guide <develop_guide_core>` for architecture context and
the repository documentation conventions when adding or changing public
documentation.

Tests
*****

Add or update a focused ``pytest`` test when changing a public contract,
runtime service, file-layout behaviour, or a regression-prone model workflow.
Tests should exercise observable behaviour and avoid requiring a real model
installation, scheduler, or large simulation data unless that environment is
explicitly under test.

Use ``tmp_path`` for isolated filesystem state and lightweight fakes or mocks
for external commands. Keep a regression test close to the failure it
protects: test a result-publication edge case through the service that publishes
it, rather than through an unrelated command-line path.

Change Scope
************

Inspect the relevant implementation, tests, configuration, and generated
resources before editing. Keep a change focused on the requested behaviour;
do not combine a repair with an unrelated architecture cleanup. When a public
workflow changes, update the matching documentation and verify its examples
against the current source.
