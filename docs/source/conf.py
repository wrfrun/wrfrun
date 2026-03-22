# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from os.path import abspath

sys.path.insert(0, abspath("../.."))

project = "wrfrun"
copyright = "2026, Syize"
author = "Syize"
release = "0.3.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

templates_path = ["_templates"]

# The main toctree document.
master_doc = "index"

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_sidebars = {
    "index": ["sidebar-nav-bs"],
    "**": ["sidebar-nav-bs"],
}

# Set up autosummary and autodoc
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "inherited-members": False,
}
autodoc_typehints = "description"
