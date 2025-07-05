# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# this needs the command sphinx-build -b html . _build/html
# and chcke with open _build/html/index.html
# it does not work with make html.
# André Csillaghy 14.6.25

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
# sys.path.insert(0, os.path.abspath('../../micropython'))
sys.path.insert(0, os.path.abspath('.'))



# -- Project information -----------------------------------------------------

project = 'goesflarewatch'
copyright = '2025'
author = 'André Csillaghy'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
]

# The suffix of source filenames.
# We use .rst files, but you can add .md if you're using Markdown as well
#source_suffix = '.rst'  # or ['.rst', '.md'] for mixed content
source_suffix = {
    '.rst': 'restructuredtext',
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

autodoc_mock_imports = ["machine", 'network', 'ujson', 'ure', 'urequests', 'micropython', 'sys']
