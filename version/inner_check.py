#!/usr/bin/env python3
"""Python script for checking Python versions"""

import argparse
import logging
import sys
from typing import NoReturn

from packaging.version import Version

import tubthumper
from util import configure_logger

logger = configure_logger(logging.getLogger(__name__))

IS_FINAL = "is_final"
CURRENT_SUPERSEDES = "current_supersedes"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Command line utility for checking Python versions"
    )
    parser.add_argument(
        "-v", "--version", help="Version to check, defaults to current version"
    )
    parser.add_argument(
        "check",
        choices=[IS_FINAL, CURRENT_SUPERSEDES],
        help="Type of check to perform",
    )
    return parser.parse_args()


def _get_current_version() -> Version:
    """Gets the current version of tubthumper"""
    curr_str = tubthumper.__version__
    return Version(curr_str)


def _is_final(ver: Version) -> NoReturn:
    if ver.is_prerelease or ver.is_postrelease:
        sys.exit(1)
    sys.exit(0)


def _current_supersedes(ver: Version) -> NoReturn:
    curr_ver = _get_current_version()
    logger.info(f"Current version: {curr_ver}")
    if curr_ver <= ver:
        sys.exit(1)
    sys.exit(0)


def main() -> None:
    """Determines if this version is a final release"""
    args = _parse_args()

    if args.version is None:
        ver = _get_current_version()
        logger.info(f"Current version: {ver}")
    else:
        ver = Version(args.version)

    if args.check == IS_FINAL:
        _is_final(ver)
    elif args.check == CURRENT_SUPERSEDES:
        _current_supersedes(ver)
    else:
        raise ValueError(f"Invalid check {args.check} provided")


if __name__ == "__main__":
    main()
