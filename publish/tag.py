#!/usr/bin/env python3
"""Python script for publishing a tag to Github"""

import argparse
import logging
import os
import pprint
import sys

from packaging.version import Version

import tubthumper

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# Setup sys.path so we can import other modules
sys.path.append(REPO_ROOT)

from util import configure_logger, request_with_retry

logger = configure_logger(logging.getLogger(__name__))


def main() -> None:
    """Pushes a git tag to Github"""
    args = _parse_args()
    version = tubthumper.__version__
    logger.info(f"Publishing tag {version} to Github")

    prerelease = _is_prerelease(version)
    if prerelease:
        logger.info("This is a prerelease")

    draft = args.draft
    if draft:
        logger.info("This is a draft release")

    changes = _get_changes(version)
    logger.info(f"Changes:\n{changes}")

    _publish_tag(version, changes, prerelease, draft)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Command line utility for tagging on Github"
    )
    parser.add_argument(
        "-d", "--draft", action="store_true", help="Publish a draft release"
    )
    return parser.parse_args()


def _is_prerelease(version: str) -> bool:
    return Version(version).is_prerelease


def _get_changes(version: str) -> str:
    search_pattern = "## Unreleased" if _is_prerelease(version) else f"## {version}"
    changes_lines = []
    with open("CHANGELOG.md", encoding="utf-8") as file_obj:
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


def _publish_tag(version: str, changes: str, prerelease: bool, draft: bool) -> None:
    payload = {
        "tag_name": version,
        "name": version,
        "body": changes,
        "prerelease": prerelease,
        "draft": draft,
    }
    auth = ("token", os.environ["GITHUB_TOKEN"])
    response = request_with_retry(
        "POST",
        "https://api.github.com/repos/matteosox/tubthumper/releases",
        headers={"accept": "application/vnd.github.v3+json"},
        auth=auth,
        json=payload,
    )
    logger.info(f"Github Response:\n{pprint.pformat(response.json())}")


if __name__ == "__main__":
    main()
