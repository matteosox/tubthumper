"""Python module with single public linkcode_resolve function"""

import inspect
import os
import shlex
import subprocess
import sys

from packaging.version import Version

import tubthumper


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
    rel_url = _get_rel_url(modname, fullname)
    blob = _get_blob()

    return f"https://github.com/matteosox/tubthumper/blob/{blob}/tubthumper/{rel_url}"


def _get_blob() -> str:
    version_str = tubthumper.__version__
    version = Version(version_str)
    if version.is_devrelease or version.is_postrelease:
        return _get_git_sha()
    return version_str


def _get_git_sha() -> str:
    completed_process = subprocess.run(
        shlex.split("git rev-parse --short HEAD"),
        check=True,
        text=True,
        capture_output=True,
    )
    return completed_process.stdout.strip()


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
