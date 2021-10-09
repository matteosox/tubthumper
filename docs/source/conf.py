"""
Configuration file for the Sphinx documentation builder.

For a full list of confiuration options, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# pylint: disable=invalid-name

import datetime
import inspect
import io
import logging
import os
import shlex
import subprocess
import sys
import zipfile
from typing import Tuple

from packaging.version import Version

import tubthumper
from util import configure_logger, request_with_retry

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


def linkcode_resolve(domain: str, info: dict) -> str:
    """
    linkcode Sphinx extension uses this function to map objects to be
    documented to external URLs where the code is kept, in our case
    github. Read more at:
    https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html
    """
    if domain != "py":
        raise ValueError(f"Not currently documenting {domain}, only Python")

    modname = info["module"]
    fullname = info["fullname"]
    rel_url = (
        "VERSION" if fullname == "__version__" else _get_rel_url(modname, fullname)
    )
    blob = "main" if "dev" in tubthumper.__version__ else tubthumper.__version__

    return f"https://github.com/matteosox/tubthumper/blob/{blob}/tubthumper/{rel_url}"


def _get_rel_url(modname: str, fullname: str) -> str:
    """Get the relative url given the module name and fullname"""
    obj = sys.modules.get(modname)
    for part in fullname.split("."):
        obj = getattr(obj, part)

    # strip decorators, which would resolve to the source of the decorator
    # possibly an upstream bug in getsourcefile, bpo-1764286
    try:
        unwrap = inspect.unwrap
    except AttributeError:
        pass
    else:
        obj = unwrap(obj)

    # Can only get source files for some Python objects
    try:
        source_file = inspect.getsourcefile(obj)
    except TypeError:
        source_file = sys.modules.get(modname).__file__
    finally:
        rel_path = os.path.relpath(
            source_file, start=os.path.dirname(tubthumper.__file__)
        )

    # Can only get source lines for some Python objects
    try:
        source, lineno = inspect.getsourcelines(obj)
    except TypeError:
        linespec = ""
    else:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"

    return f"{rel_path}{linespec}"


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


# -- Read the Docs runs main to grab the reports artifact from Github --------

logger = configure_logger(logging.getLogger(__name__))

GITHUB_HEADERS = {"accept": "application/vnd.github.v3+json"}
PER_PAGE = 100
ARTIFACTS_URL = "https://api.github.com/repos/matteosox/tubthumper/actions/artifacts"
GET = "GET"


def _get_git_sha() -> str:
    completed_process = subprocess.run(
        shlex.split("git rev-parse --short HEAD"),
        check=True,
        text=True,
        capture_output=True,
    )
    return completed_process.stdout.strip()


def _get_auth_header() -> Tuple[str, str]:
    return ("token", os.environ["GITHUB_TOKEN"])


class ArtifactNotFoundError(Exception):
    """Thrown when an artifact can't be found"""


@tubthumper.retry_decorator(
    exceptions=ArtifactNotFoundError, exponential=1, init_backoff=30, jitter=False
)
def _get_reports_artifact_id(git_sha: str) -> int:
    auth = _get_auth_header()
    name = f"reports_{git_sha}"
    page = 1
    while True:
        params = {"page": page, "per_page": PER_PAGE}
        response = request_with_retry(
            GET,
            ARTIFACTS_URL,
            headers=GITHUB_HEADERS,
            params=params,
            auth=auth,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        for artifact in result["artifacts"]:
            if artifact["name"] == name:
                return artifact["id"]
        if result["total_count"] < PER_PAGE:
            raise ArtifactNotFoundError(
                f"Could not find reports artifact for git_sha {git_sha}"
            )
        page += 1


def _dir_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def _download_artfact(artifact_id: int) -> None:
    auth = _get_auth_header()
    response = request_with_retry(
        GET,
        f"{ARTIFACTS_URL}/{artifact_id}/zip",
        auth=auth,
        timeout=10,
    )
    response.raise_for_status()
    destination = os.path.join(_dir_path(), "_static", "reports")
    with zipfile.ZipFile(io.BytesIO(response.content)) as myzip:
        myzip.extractall(path=destination)


def main() -> None:
    """Downloads reports artifact from Github for corresponding git sha"""
    logger.info("Getting reports from Github")
    git_sha = _get_git_sha()
    logger.info(f"Determining artifacts id for git sha {git_sha}")
    artifact_id = _get_reports_artifact_id(git_sha)
    logger.info(f"Downloading artifact with id {artifact_id}")
    _download_artfact(artifact_id)


if os.environ.get("READTHEDOCS") == "True":
    main()
