"""
Configuration file for the Sphinx documentation builder.

For a full list of confiuration options, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# pylint: disable=invalid-name, import-error

import datetime
import doctest
import os
import sys

from packaging.version import Version

import tubthumper


def _dir_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))


# Setup sys.path so we can import other modules
sys.path.append(os.path.join(_dir_path(), ".."))
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
nitpick_ignore = [("py:class", "tubthumper._types.T")]


# -- Extension configuration -------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinxext.opengraph",
]

# Show typehints as content of the function or method The typehints of
# overloaded functions or methods will still be represented in the
# signature.
autodoc_typehints = "description"

# Add links to modules and objects in the Python standard library documentation
intersphinx_mapping = {
    "https://docs.python.org/3": None,
}

# Default flags for testing `doctest` directives used by the
# `sphinx.ext.doctest` Sphinx extension
doctest_default_flags = doctest.DONT_ACCEPT_TRUE_FOR_1 | doctest.ELLIPSIS

# Python code that is treated like it were put in a testsetup directive for
# every file that is tested, and for every group.
doctest_global_setup = """
import logging
import random
import time

random.seed(0)  # consistent behavior
time.sleep = lambda arg: None  # don't actually sleep

# Doctest only captures prints, not logging to stdout, so
# we have to add a handler that prints to tubthumper's logger
logger = logging.getLogger("tubthumper")


class PrintHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        print(msg)


print_handler = PrintHandler()
formatter = logging.Formatter("%(levelname)s: %(message)s")
print_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(print_handler)

"""

# We don't need warnings about non-consecutive header level
suppress_warnings = ["myst.header"]

# The `sphinx.ext.linkcode` extension returns the URL to source code
# corresponding to the object referenced.
linkcode_resolve = linkcode.linkcode_resolve

# sphinxext-opengraph settings
ogp_site_url = "https://tubthumper.mattefay.com"
ogp_site_name = f"Tubthumper {tubthumper.__version__}"
ogp_image = "https://tubthumper.mattefay.com/en/latest/_static/logo.png"
ogp_image_alt = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": True,
}

# Path to the logo placed at the top of the sidebar
html_logo = "_static/logo.png"

html_title = f"Tubthumper {tubthumper.__version__}"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Hide link to each page's source file in the footer.
html_show_sourcelink = False


# -- Build the readme --------------------------------------------------------


def build_readme():
    """Copy README.md over, in the process adding doctests"""
    with open(
        os.path.join(_dir_path(), "..", "..", "README.md"), encoding="utf-8"
    ) as source:
        readme = source.read()

    dest_dir = os.path.join(_dir_path(), "..", "build")
    try:
        os.mkdir(dest_dir)
    except FileExistsError:
        pass

    with open(os.path.join(dest_dir, "readme.md"), "w", encoding="utf-8") as dest:
        dest.write(readme.replace("```python\n>>> ", "```{doctest}\n>>> "))


build_readme()


# -- Read the Docs runs this to grab the reports artifact from Github --------

if os.environ.get("READTHEDOCS") == "True":
    download_reports()
