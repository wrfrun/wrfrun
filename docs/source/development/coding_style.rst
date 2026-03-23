``wrfrun`` Project Coding Style
###############################

This document describes the coding style guidelines for the ``wrfrun`` project. 
All contributions must adhere to these guidelines to maintain consistency across the codebase.

We use `Ruff <https://docs.astral.sh/ruff/>`_ for all code linting and formatting. 
Ruff is configured in the ``pyproject.toml`` file, and all code must pass Ruff checks before being merged.

Quick Start
***********

Before submitting code, run these commands to ensure your code follows the style guidelines:

.. code-block:: bash

    # Format your code automatically
    ruff format wrfrun
    
    # Check for linting errors
    ruff check wrfrun
    
    # Automatically fix fixable errors
    ruff check --fix wrfrun

These commands will handle most style issues automatically. For issues that cannot be fixed automatically, Ruff will provide a description of the problem and its location.

General Principles
******************

- **Readability over brevity**: Code is read more often than it is written. Prioritize clarity and readability.
- **Consistency**: Follow the existing style in the file you're modifying, even if it differs from these guidelines.
- **Pythonic**: Write idiomatic Python code that follows standard practices.
- **Document your code**: All public APIs, classes, and functions must have proper documentation.

Code Formatting
***************

Line Length
===========

- Maximum line length is **130 characters**.
- This allows for more code on screen while still maintaining readability.
- Long strings, URLs, and comments can exceed this limit if necessary.

Indentation
===========

- Use **4 spaces** for indentation (no tabs).
- Vertically align similar elements when it improves readability.
- Indent hanging parentheses by 4 spaces, not aligned to the opening parenthesis.

.. code-block:: python
    :caption: ✅ Good

    def function_with_many_args(
        arg1: int,
        arg2: str,
        arg3: bool,
    ) -> None:
        if (
            some_long_condition
            and another_long_condition
            and third_long_condition
        ):
            do_something()

.. code-block:: python
    :caption: ❌ Bad

    def function_with_many_args(arg1: int,
                               arg2: str,
                               arg3: bool) -> None:
        if some_long_condition and \
           another_long_condition and \
           third_long_condition:
            do_something()

Quotes
======

- Use **double quotes** for strings by default.
- Use single quotes only if the string contains double quotes that would otherwise need escaping.

.. code-block:: python
    :caption: ✅ Good

    message = "Hello, World!"
    quote = 'He said, "Hello!"'

.. code-block:: python
    :caption: ❌ Bad

    message = 'Hello, World!'
    quote = "He said, \"Hello!\""

Trailing Commas
===============

- Always add a trailing comma to the last element in multi-line lists, dicts, tuples, and function signatures.
- This makes it easier to add or remove elements later without modifying the previous line.

.. code-block:: python
    :caption: ✅ Good

    my_list = [
        "item1",
        "item2",
        "item3",  # Trailing comma
    ]

Naming Conventions
******************

Follow standard Python naming conventions from `PEP 8 <https://peps.python.org/pep-0008/#naming-conventions>`_:

- **Classes**: Use ``PascalCase`` (e.g., ``WRFRunConfig``, ``ExecutableBase``)
- **Functions and methods**: Use ``snake_case`` (e.g., ``get_model_config``, ``write_namelist``)
- **Variables and constants**: Use ``snake_case`` (e.g., ``output_path``, ``core_num``)
- **Module-level constants**: Use ``UPPER_SNAKE_CASE`` (e.g., ``WRFRUN_TEMP_PATH``, ``DEFAULT_CONFIG``)
- **Private members**: Prefix with an underscore (e.g., ``_internal_method``, ``_private_variable``)

Type Hints
**********

All public functions, methods, and variables must have type hints. Type hints improve code readability and enable static type checking.

.. code-block:: python
    :caption: ✅ Good

    def calculate_area(width: float, height: float) -> float:
        return width * height
    
    def get_config(model_name: str) -> dict[str, Any]:
        ...

.. code-block:: python
    :caption: ❌ Bad

    def calculate_area(width, height):
        return width * height
    
    def get_config(model_name):
        ...

Special Cases:

- For complex types, import from ``typing`` module
- Use ``|`` for union types (Python 3.10+ syntax) instead of ``Union[]``
- Use ``TypedDict`` for complex dictionary structures

Imports
*******

Imports are automatically sorted by Ruff. Follow these rules:

1. **Group imports** in the following order, separated by a blank line:

   - Standard library imports
   - Third-party library imports
   - Local wrfrun imports

2. **Import style**:

   - Prefer relative imports for internal imports within the same module
   - Use absolute imports only when relative imports would be too deeply nested or are not feasible
   - Avoid wildcard imports (``from module import *``) except for module ``__init__.py`` files
   - Group multiple imports from the same module in parentheses if they don't fit on one line

.. code-block:: python
    :caption: ✅ Good

    import os
    import sys
    from typing import Any, Optional

    import tomli
    import tomli_w

    # Relative import within the same module
    from ._config import WRFRunConfig
    from .error import ConfigError, ModelNameError
    
    # Absolute import for external modules
    from wrfrun.extension.utils import extension_helper

.. code-block:: python
    :caption: ❌ Bad

    import os, sys
    from typing import *
    
    from ._config import WRFRunConfig
    from wrfrun.core import *

Documentation Strings
*********************

All public classes, methods, and functions must have docstrings. We use the **Sphinx/reStructuredText style docstring** format, which is natively supported by the documentation generator.

Docstring Requirements:

- Start with a short, one-line summary of what the function/class does
- Include a longer description if needed to explain behavior, edge cases, or implementation details
- Document all parameters with ``:param name: description``
- Include parameter type with ``:type name: type``
- Document the return value with ``:return: description`` (if not ``None``)
- Include return type with ``:rtype: type``
- Document exceptions that may be raised with ``:raises ExceptionType: description``

.. code-block:: python
    :caption: ✅ Good

    def get_model_config(self, model_name: str) -> dict:
        """
        Get the configuration for a specific model.
        
        :param model_name: Name of the model to get configuration for (e.g., "wrf", "palm")
        :type model_name: str
        :return: Dictionary containing the model configuration
        :rtype: dict
        :raises ModelNameError: If the specified model is not found in the configuration
        """
        if model_name not in self["model"]:
            raise ModelNameError(f"Model '{model_name}' not found")
        return self["model"][model_name]

Code Comments
=============

- Add comments to explain *why* you're doing something, not *what* you're doing
- Keep comments concise and up-to-date
- Avoid redundant comments that just restate the code
- Use inline comments sparingly, only for non-obvious logic

Linting Rules
*************

Ruff is configured with the following rule sets:

- ``D``: Docstring rules (pydocstyle)
- ``E``: Error rules (pycodestyle)
- ``F``: Pyflakes rules (for detecting bugs)
- ``I``: Import sorting rules (isort)

The following rules are explicitly ignored:

- ``F403``: Allow wildcard imports in __init__.py files
- ``D200``: Allow single-line docstrings to end with a period
- ``D203``: Allow one blank line before class docstrings
- ``D205``: Allow one blank line between summary and description
- ``D211``: Allow no blank line before class docstrings
- ``D212``: Allow multi-line docstrings to start on the first line
- ``D400``: Allow docstrings to not end with a period
- ``D401``: Allow docstrings to not start with "Returns" etc.
- ``D404``: Allow docstrings to not have a "Returns" section if it's obvious
- ``D415``: Allow docstrings to end with a period even if they have a "Returns" section

You can see the full configuration in ``pyproject.toml`` under the ``[tool.ruff]`` section.

Best Practices
**************

1. **Keep functions small**: Each function should do one thing and do it well. If a function is longer than ~50 lines, consider splitting it into smaller functions.
2. **Avoid global variables**: Use class variables or pass values as parameters instead. The only allowed global variable is the ``WRFRUN`` singleton.
3. **Use context managers**: For resources that need to be cleaned up, use context managers or ensure proper cleanup in finally blocks.
4. **Error handling**:
   - Raise appropriate exceptions instead of returning None or error codes
   - Use descriptive error messages that help users understand what went wrong
   - Log errors with enough context to help with debugging
5. **Performance considerations**:
   - Optimize only when necessary, based on profiling results
   - Avoid premature optimization that makes code harder to read
   - For performance-critical sections, add comments explaining the optimization
6. **Backward compatibility**:
   - Maintain backward compatibility for public APIs whenever possible
   - If breaking changes are necessary, deprecate the old API first and provide a migration path

Automated Checks
****************

If you're using VS Code, install the Ruff extension to get real-time feedback as you write code.

If you have questions about any of these guidelines, feel free to ask in your pull request or open an issue for clarification.
