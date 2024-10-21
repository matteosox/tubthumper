"""Unit tests for the function retry_decorator"""

import time
import unittest
from types import MethodType
from typing import Any, Optional, Union

from mock import AsyncMock, Mock

# asyncio event loop uses the "monotonic" timer,
# and we profile it using the "perf_counter" timer
TIMER_RESOLUTION = (
    time.get_clock_info("monotonic").resolution
    + time.get_clock_info("perf_counter").resolution
)
TIMING_OVERHEAD = 200e-3  # 200 ms


def assert_time(
    test_case: unittest.TestCase, duration: float, expected_duration: float
) -> None:
    """Assert a timer is within the expected duration, plus a small overhead"""
    test_case.assertGreater(duration, expected_duration - TIMER_RESOLUTION)
    test_case.assertLess(
        duration, expected_duration + TIMING_OVERHEAD + TIMER_RESOLUTION
    )


def create_method_mock(
    *args: Any, async_mock: bool = False, **kwargs: Any
) -> Union[Mock, AsyncMock]:
    """Mocks a proper function descriptor that will bind to a class like a proper method"""

    Method = AsyncMock if async_mock else Mock
    method = Method(*args, **kwargs)

    def get(
        self: Union[Mock, AsyncMock], obj: Optional[object], objtype: Optional[type]
    ) -> Union[AsyncMock, Mock, MethodType]:
        return self if obj is None else MethodType(self, obj)

    method.__get__ = get
    return method


def timed_mock(
    *args: Any, async_mock: bool = False, **kwargs: Any
) -> Union[Mock, AsyncMock]:
    """
    Create a mock that keeps track of when it was called
    then throws a TEST_EXCEPTION
    """
    call_times = []

    wrapped_mock = Mock(side_effect=kwargs.get("side_effect"))

    def side_effect(*inner_args: Any, **inner_kwargs: Any):
        call_times.append(time.perf_counter())
        return wrapped_mock(*inner_args, **inner_kwargs)

    kwargs["side_effect"] = side_effect
    MyMock = AsyncMock if async_mock else Mock
    mock = MyMock(*args, **kwargs)
    mock.call_times = call_times
    return mock


def get_a_func():
    """Returns a generic function"""

    def func(one: bool, two: int, *, three: float = 3.0) -> complex:
        """This is a docstring"""
        return 1

    return func


def get_an_async_func():
    """Returns a generic async function"""

    async def async_func(one: bool, two: int, *, three: float = 3.0) -> complex:
        """This is a docstring"""
        return 1

    return async_func
