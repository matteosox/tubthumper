"""Test suite for _version module"""

import unittest

from packaging.version import Version

import tubthumper
from tubthumper import _version


class TestVersion(unittest.TestCase):
    """Test the _version module"""

    def test_version(self):
        """Test the version string"""
        Version(_version.version)
        self.assertEqual(tubthumper.__version__, _version.version)


if __name__ == "main":
    unittest.main()
