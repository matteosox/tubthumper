#!/usr/bin/env python3
"""Python script for pushing a git tag to Github"""

import datetime
import logging
import os

from packaging.version import Version

import tubthumper
from util import configure_logger, request_with_retry

logger = configure_logger(logging.getLogger(__name__))


def main() -> None:
    """Pushes a git tag to Github"""
    version = tubthumper.__version__
    if not _should_tag(version):
        logger.info(f"Not tagging {version} since it is not a final or prerelease")
        return

    logger.info(f"Publishing tag {version} to Github")

    auth = ("token", os.environ["GITHUB_TOKEN"])
    payload = {
        "tag_name": version,
        "name": version,
        "body": _get_changes(version),
        "prerelease": _is_prerelease(version),
    }
    request_with_retry(
        "POST",
        "https://api.github.com/repos/matteosox/tubthumper/releases",
        headers={"accept": "application/vnd.github.v3+json"},
        auth=auth,
        json=payload,
    )


def _should_tag(version_str: str) -> bool:
    version = Version(version_str)
    return not (version.is_devrelease or version.is_postrelease)


def _is_prerelease(version: str) -> bool:
    return Version(version).is_prerelease


def _get_changes(version: str) -> str:
    search_pattern = f"## {version}"
    if _is_prerelease(version):
        search_pattern = "## Unreleased"

    date = datetime.datetime.now().date()
    changes_lines = [f"## {version} ({date})"]

    with open("docs/source/CHANGELOG.md", encoding="utf-8") as file_obj:
        for line in file_obj:
            if line.startswith(search_pattern):
                break
        else:
            raise Exception(f"Could not find {search_pattern} in CHANGELOG.md")

        for line in file_obj:
            if line.startswith("## "):
                break
            changes_lines.append(line)

    return "".join(changes_lines)


if __name__ == "__main__":
    main()
