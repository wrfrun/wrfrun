# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from os.path import abspath
sys.path.insert(0, abspath("../.."))

project = 'wrfrun'
copyright = '2025, Syize'
author = 'Syize'
release = '0.1.7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    'sphinx_copybutton',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']

# The main toctree document.
master_doc = 'index'

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']

html_sidebars = {
    "index": ["sidebar-nav-bs"],
    "**": ["sidebar-nav-bs"],
}

# Set up autosummary and autodoc
autosummary_generate = True
autodoc_default_options = {
    'inherited-members': None,
}
autodoc_typehints = 'description'


# Skip the doc of specific members in wrfrun when autodoc collecting docs.
# def skip_specific_members(app, what, name, obj, skip, options):
#     """
#     See `sphinx docs <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#skipping-members>`_.
#
#     :param app:
#     :type app:
#     :param what:
#     :type what:
#     :param name:
#     :type name:
#     :param obj:
#     :type obj:
#     :param skip:
#     :type skip:
#     :param options:
#     :type options:
#     :return:
#     :rtype:
#     """
#     print(f"what is {what}, name is {name}, obj is {type(obj)}")
#     return skip
#
#
# def setup(app):
#     """
#     Set handlers.
#
#     :param app:
#     :type app:
#     :return:
#     :rtype:
#     """
#     app.connect("autodoc-skip-member", skip_specific_members)
