"""Module for accessing the version"""

from pkg_resources import resource_stream


def _get_version() -> str:
    """Returns a version string"""
    with resource_stream("tubthumper", "VERSION") as version_file:
        return version_file.read().decode("utf-8").strip()


version = _get_version()
