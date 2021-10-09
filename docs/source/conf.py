"""
Configuration file for the Sphinx documentation builder.

For a full list of confiuration options, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# pylint: disable=invalid-name

import datetime
import os
import sys

from packaging.version import Version

import tubthumper


def _dir_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))


# Setup sys.path so we can import other modules
sys.path.append(os.path.join(_dir_path()))
sys.path.append(os.path.join(_dir_path(), "..", ".."))

import linkcode
from download_reports import download_reports

# -- Project information -----------------------------------------------------

project = "Tubthumper"
author = "Matt Fay"
copyright = f"2021-{datetime.datetime.now().year}, {author}"  # pylint: disable=redefined-builtin

# The full version, including alpha/beta/rc tags
release = tubthumper.__version__
_version = Version(release)
version = f"{_version.major}.{_version.minor}.{_version.micro}"


# -- General configuration ---------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Pygments style to use for highlighting when the CSS media query
# (prefers-color-scheme: dark) evaluates to true.
pygments_dark_style = "monokai"

# Sphinx warns about all references where the target cannot be found, except
# those explicitly ignored.
nitpicky = True
nitpick_ignore = [("py:class", "tubthumper._types.ReturnType")]


# -- Extension configuration -------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
]

# Show typehints as content of the function or method The typehints of
# overloaded functions or methods will still be represented in the
# signature.
autodoc_typehints = "description"

# Add links to modules and objects in the Python standard library documentation
intersphinx_mapping = {
    "https://docs.python.org/3": None,
}

# We don't need warnings about non-consecutive header level
suppress_warnings = ["myst.header"]

# The `sphinx.ext.linkcode` extension returns the URL to source code
# corresponding to the object referenced.
linkcode_resolve = linkcode.linkcode_resolve


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"
html_title = tubthumper.__version__
html_logo = "_static/logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Read the Docs runs this to grab the reports artifact from Github --------

if os.environ.get("READTHEDOCS") == "True":
    download_reports()
