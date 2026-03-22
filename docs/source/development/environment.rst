Development Environment Setup
#############################

This guide will help you set up a complete development environment for contributing to ``wrfrun``. 
A proper development environment ensures you can run tests, build documentation, and use all the development tools configured for the project.

Prerequisites
*************

Before setting up the development environment, make sure you have:

- **Python 3.10 or newer**: ``wrfrun`` requires Python 3.10+
- **Git**: For cloning the repository and version control
- **Linux operating system**: While ``wrfrun`` may work on other platforms, it is primarily developed and tested on Linux
- **A C compiler (optional)**: For building any optional C extensions

Getting the Source Code
***********************

First, clone the ``wrfrun`` repository from GitHub:

.. code-block:: bash

    git clone https://github.com/wrfun/wrfrun.git
    cd wrfrun

If you plan to contribute changes, you should first fork the repository and then clone your fork:

.. code-block:: bash

    git clone https://github.com/YOUR_USERNAME/wrfrun.git
    cd wrfrun

Setting Up the Development Environment
**************************************

``wrfrun`` uses modern Python packaging tools. 
We recommend using `uv <https://docs.astral.sh/uv/>`_ for dependency management, but you can also use ``pip``.

Using uv (Recommended)
======================

`uv <https://docs.astral.sh/uv/>`_ is a fast Python package installer and resolver. 
If you don't have it installed, you can refer to `uv's website <https://docs.astral.sh/uv/>`_ and install it.

Once you have `uv <https://docs.astral.sh/uv/>`_ installed, create a virtual environment and install the development dependencies:

.. code-block:: bash

    # This will install all dependencies
    uv sync

Using pip
=========

If you prefer using ``pip``, you can set up the environment with:

.. code-block:: bash

    # Create a virtual environment
    python -m venv .venv
    
    # Activate the virtual environment
    source .venv/bin/activate  # On Linux/macOS
    # Or on Windows: .venv\Scripts\activate
    
    # Install the package in editable mode with development dependencies
    pip install -e ".[dev]"

Verifying the Installation
**************************

To verify your development environment is set up correctly, you can:

1. Check that you can import ``wrfrun``:

.. code-block:: bash

    python -c "import wrfrun; print(f'wrfrun version: {wrfrun.__version__}')"

2. Run the code quality tools:

.. code-block:: bash

    # Run Ruff for linting and formatting checks
    ruff check wrfrun

Development Tools
*****************

``wrfrun`` uses several development tools to ensure code quality. Here's what's included:

Code Linting and Formatting
============================

- **Ruff**: A fast Python linter and formatter
  - Lints code for common errors and style issues
  - Formats code according to the project's style guidelines
  - Configuration in ``pyproject.toml`` under ``[tool.ruff]``

.. code-block:: bash

    # Check for linting issues
    ruff check wrfrun
    
    # Automatically fix fixable issues
    ruff check --fix wrfrun
    
    # Format code
    ruff format wrfrun

Type Checking
=============

- **Pyright**: A static type checker for Python
  - Ensures type annotations are correct
  - Catches type-related bugs early
  - Configuration in ``pyproject.toml`` under ``[tool.pyright]``

.. code-block:: bash

    # Run type checking
    pyright

Documentation Building
======================

- **Sphinx**: The documentation generator
- **pydata-sphinx-theme**: The documentation theme
- **sphinx-copybutton**: Adds copy buttons to code blocks
- **sphinx-design**: For designing beautiful documentation components
- **sphinx-autobuild**: For live-reloading documentation during development

.. code-block:: bash

    # Build the documentation
    cd docs
    make html
    
    # Or build with live reloading (for development)
    sphinx-autobuild source build

Building the Package
********************

To build the package for distribution:

.. code-block:: bash

    # Build the package
    uv build
    
    # The built packages will be in the dist/ directory
    ls dist/

IDE Configuration
*****************

While you can use any text editor or IDE for development, here are some recommendations:

Visual Studio Code
==================

If you use VS Code, you can install the following extensions for the best development experience:

- **Python**: For Python language support
- **Ruff**: For Ruff integration
- **Pylance**: For Pyright integration (optional, since Pyright is already configured)

Create a ``.vscode/settings.json`` file with these settings:

.. code-block:: json

    {
        "python.linting.enabled": false,
        "python.formatting.provider": "none",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        },
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff"
        }
    }

Other Editors
=============

For other editors, refer to their documentation on how to integrate Ruff and Pyright.

Development Workflow
********************

Here's a typical development workflow for contributing to ``wrfrun``:

1. **Create a feature branch**:

.. code-block:: bash

    git checkout -b feature/my-awesome-feature

2. **Make your changes**: Write code, tests, and documentation.

3. **Run quality checks**:

.. code-block:: bash

    ruff check wrfrun
    ruff format wrfrun

4. **Commit your changes**:

.. code-block:: bash

    git add .
    git commit -m "Add my awesome feature"

5. **Push and create a Pull Request**:

.. code-block:: bash

    git push origin feature/my-awesome-feature

Then go to GitHub and create a Pull Request from your branch.

Troubleshooting
***************

If you encounter issues setting up your development environment:

- Make sure you're using Python 3.10 or newer
- Try deleting the ``.venv`` directory and recreating the virtual environment
- Check that you're in the correct directory when running commands
- For documentation building issues, check that you have all the documentation dependencies installed

If you're still having problems, feel free to open an issue on the `GitHub repository <https://github.com/wrfrun/wrfrun/issues>`_.
