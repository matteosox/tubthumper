#!/usr/bin/env python3
"""Python script for determining whether or not to release the package"""

from packaging.version import Version

import tubthumper


def main() -> None:
    """Determines if this version should be released"""
    version = Version(tubthumper.__version__)
    print(not (version.is_devrelease or version.is_postrelease))


if __name__ == "__main__":
    main()
