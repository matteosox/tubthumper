"""Test suite for _version module"""

import unittest

from packaging.version import Version

import tubthumper


class TestVersion(unittest.TestCase):
    """Test the _version module"""

    def test_version(self):
        """Test the version string"""
        Version(tubthumper.__version__)
