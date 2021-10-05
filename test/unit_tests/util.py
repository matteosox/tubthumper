"""Unit tests for the function retry_decorator"""

import time
from types import MethodType

from mock import AsyncMock, Mock

TIMING_OVERHEAD = 200e-3  # 200 ms
TIMING_UNDERHEAD = 1e-3  # 1 ms


def assert_time(test_case, duration, expected_duration):
    """Assert a timer is within the expected duration, plus a small overhead"""
    test_case.assertGreater(duration, expected_duration - TIMING_UNDERHEAD)
    test_case.assertLess(duration, expected_duration + TIMING_OVERHEAD)


def create_method_mock(*args, async_mock=False, **kwargs):
    """Mocks a proper function descriptor that will bind to a class like a proper method"""

    Method = AsyncMock if async_mock else Mock
    method = Method(*args, **kwargs)
    method.__code__ = (lambda: ...).__code__  # Necessary for inspect <3.8
    method.__get__ = (
        lambda self, obj, objtype=None: self if obj is None else MethodType(self, obj)
    )
    return method


def timed_mock(*args, async_mock=False, **kwargs):
    """
    Create a mock that keeps track of when it was called
    then throws a TEST_EXCEPTION
    """
    call_times = []

    wrapped_mock = Mock(side_effect=kwargs.get("side_effect"))

    def side_effect(*inner_args, **inner_kwargs):
        call_times.append(time.perf_counter())
        return wrapped_mock(*inner_args, **inner_kwargs)

    kwargs["side_effect"] = side_effect
    MyMock = AsyncMock if async_mock else Mock
    mock = MyMock(*args, **kwargs)
    mock.call_times = call_times
    return mock


def get_a_func():
    """Returns a generic function"""

    def func(  # pylint: disable=unused-argument
        one: bool, two: int, *, three: float = 3.0
    ) -> complex:
        """This is a docstring"""

    func.monkey_patch = True
    return func


def get_an_async_func():
    """Returns a generic async function"""

    async def async_func(  # pylint: disable=unused-argument
        one: bool, two: int, *, three: float = 3.0
    ) -> complex:
        """This is a docstring"""

    return async_func
