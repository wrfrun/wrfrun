Development Environment
#######################

This page sets up a local environment for changing ``wrfrun`` itself. It is
separate from the numerical-model installations and large input data required
to run ARPS, WRF, PALM, or another supported model. Most unit tests and the
documentation build do not require those external installations.

Prerequisites
*************

- Python 3.10 or newer, matching the minimum version in ``pyproject.toml``.
- Git, to obtain and manage the source checkout.
- `uv <https://docs.astral.sh/uv/>`_, the supported environment and dependency
  manager for this repository.
- Graphviz's ``dot`` command when building documentation that contains
  diagrams.

Linux is the primary development platform. The project may run elsewhere, but
the configured Pyright platform and model-execution workflows are maintained
on Linux.

Get the source
**************

Clone the repository, then enter its root directory:

.. code-block:: console

   $ git clone https://github.com/Syize/wrfrun.git
   $ cd wrfrun

For a contribution from a fork, clone that fork instead and add the upstream
repository as a separate remote if needed. Keep project-specific changes on a
dedicated branch rather than editing the default branch directly.

Create the environment
**********************

``uv sync`` creates or updates the local virtual environment from
``pyproject.toml`` and ``uv.lock``. It includes the development dependency
group, which supplies Ruff, Pyright, pytest, and the Sphinx extensions used by
the documentation.

.. code-block:: console

   $ uv sync

Run project tools through ``uv run`` so they use that environment:

.. code-block:: console

   $ uv run wrfrun --version
   wrfrun 0.5.2

The displayed version depends on the installed project metadata, so it may be
different in another checkout. The command proves that the CLI entry point is
available; it does not prove that an external numerical model is installed.

Routine checks
**************

Use the narrowest relevant test while developing, then run the shared checks
before handing off a change:

.. code-block:: console

   $ uv run ruff format --check wrfrun tests
   $ uv run ruff check wrfrun tests
   $ uv run pyright
   $ uv run pytest

Ruff can apply mechanical fixes when appropriate:

.. code-block:: console

   $ uv run ruff format wrfrun tests
   $ uv run ruff check --fix wrfrun tests

The project's style and scope conventions are described in
:doc:`Coding style <coding_style>`.

Build the documentation
***********************

Build the site from the repository root. The output is intentionally outside
``docs/source`` and must not be edited by hand:

.. code-block:: console

   $ uv run sphinx-build -b html docs/source docs/build/html

For a quick syntax, toctree, and cross-reference check without producing an
HTML site, use Sphinx's dummy builder:

.. code-block:: console

   $ uv run sphinx-build -b dummy docs/source /tmp/wrfrun-docs

If a page contains a Graphviz diagram, ensure ``dot`` is on ``PATH`` before
building. See :doc:`Coding style <coding_style>` for module docstring and API
reference conventions.

Build a distribution
********************

``wrfrun`` uses Meson through ``meson-python`` as its build backend. Build a
wheel and source distribution with:

.. code-block:: console

   $ uv build

The generated artifacts are placed in ``dist/``. Building a distribution is
especially useful after changing ``meson.build`` files or bundled resources;
a source checkout can find files that an installed package is missing.

External model prerequisites
****************************

Unit tests use temporary files and controlled command doubles. A real
simulation additionally needs the selected model's compiled binaries,
installation-specific tables, input data, and—when applicable—a configured
scheduler. Those requirements belong to the model integration and project
configuration, not to the base Python development environment.

See :doc:`Model development <develop_guide_model>` when changing model
integration, or the user-facing :doc:`installation guide </usage/installation>`
when preparing a simulation project.
