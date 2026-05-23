# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Ajoute le dossier src au PYTHONPATH
sys.path.insert(0, os.path.abspath('../src'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'msunpv'
copyright = '2026, Franck VANHOUCKE'
author = 'Franck VANHOUCKE'
release = '1.0.0'
version = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Core autodoc — generates API docs from docstrings
    "sphinx.ext.autodoc",
    # "View source" links on every class/function page
    "sphinx.ext.viewcode",
    # Support for Google-style and NumPy-style docstrings
    "sphinx.ext.napoleon",
    # Cross-references to the Python standard library
    "sphinx.ext.intersphinx",
    # Autosummary tables (used in modules.rst)
    "sphinx.ext.autosummary",
    # :todo: directives support
    "sphinx.ext.todo",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- autodoc options ---------------------------------------------------------
# Show both class docstring and __init__ docstring
autoclass_content = 'both'
# Document members in source-code order
autodoc_member_order = 'bysource'
# Show type annotations in signature
autodoc_typehints = 'description'

# -- napoleon options --------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# -- intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
}

# -- todo --------------------------------------------------------------------
todo_include_todos = True

# -- autosummary -------------------------------------------------------------
autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = []

# -- Theme options -----------------------------------------------------------
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
}

# -- Display Version ----------------------------------------------------------
rst_epilog = """
.. |release| replace:: %s
""" % release