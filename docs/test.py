"""Module for testing documentation"""

import logging
import random
import time
from types import ModuleType

from tubthumper import _retry_factory


def setup():
    """
    Function for shared doctest setup, must be idempotent,
    since different doctest files will run it in the same
    Python process.
    """
    random.seed(0)
    _setup_sleep()
    _setup_logging()


def _setup_sleep():
    """
    Mock _retry_factory's time module with an "insomniac"
    version where sleep doesn't actually sleep to speed up tests.
    """

    _retry_factory.time = _InsomniaTime(time.__name__)


class _InsomniaTime(ModuleType):
    """Mocked time module"""

    @staticmethod
    def sleep(_):
        """Don't sleep"""

    def __getattr__(self, name):
        return getattr(time, name)


class _PrintHandler(logging.Handler):
    """Simple logging handler that uses the print function"""

    def emit(self, record):
        """Format a record into a message and print it"""
        msg = self.format(record)
        print(msg)


def _setup_logging():
    """
    Doctest only captures prints, not logging to stdout, so
    we have to add a printing handler to tubthumper's logger
    """
    logger = logging.getLogger("tubthumper")

    if not logger.hasHandlers():
        print_handler = _PrintHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        print_handler.setFormatter(formatter)
        logger.addHandler(print_handler)
