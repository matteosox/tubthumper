"""Module defining the retry_factory function"""

import asyncio
import random
import time
from dataclasses import dataclass
from functools import update_wrapper
from typing import Any, Callable, overload

from tubthumper import _types
from tubthumper._types import AwaitableCallable, RetryCallable, T

__all__ = ["RetryError"]


class RetryError(Exception):
    """Exception raised when a retry or time limit is reached"""


@dataclass(frozen=True)
class RetryConfig:
    """Config class for retry logic"""

    exceptions: _types.Exceptions
    retry_limit: _types.RetryLimit
    time_limit: _types.TimeLimit
    init_backoff: _types.InitBackoff
    exponential: _types.Exponential
    jitter: _types.Jitter
    reraise: _types.Reraise
    log_level: _types.LogLevel
    logger: _types.Logger


Backoff = float


class _RetryHandler:
    """Class for handling exceptions to be retried"""

    exceptions: _types.Exceptions
    _retry_config: RetryConfig
    _timeout: float
    _count: int
    _backoff: Backoff
    _unjittered_backoff: Backoff

    def __init__(self, retry_config: RetryConfig):
        self.exceptions = retry_config.exceptions
        self._retry_config = retry_config

        self._calc_backoff: Callable[[], Backoff]
        if self._retry_config.jitter:
            self._calc_backoff = lambda: self._unjittered_backoff * random.random()
        else:
            self._calc_backoff = lambda: self._unjittered_backoff

    def start(self) -> None:
        """Initialize the retry handler's timeout, count, and backoff"""
        self._timeout = time.perf_counter() + self._retry_config.time_limit
        self._count = 0
        self._unjittered_backoff = self._retry_config.init_backoff

    def handle(self, exc: Exception) -> float:
        """
        Handles the exception, either:
        (a) raising a RetryError (or the exception provided), or
        (b) returning a backoff duration to sleep, logging the caught exception
        """
        self._increment()
        self._check_retry_limit(exc)
        self._check_time_limit(exc)
        self._retry_config.logger.log(
            self._retry_config.log_level,
            f"Function threw exception below on try {self._count}, "
            f"retrying in {self._backoff:n} seconds",
            exc_info=True,
        )
        return self._backoff

    def _increment(self) -> None:
        """Increment the retry handler's count and backoff duration"""
        self._count += 1
        self._backoff = self._calc_backoff()
        self._unjittered_backoff *= self._retry_config.exponential

    def _check_retry_limit(self, exc: Exception) -> None:
        if self._count > self._retry_config.retry_limit:
            if self._retry_config.reraise:
                raise exc
            raise RetryError(
                f"Retry limit {self._retry_config.retry_limit} reached"
            ) from exc

    def _check_time_limit(self, exc: Exception) -> None:
        if (time.perf_counter() + self._backoff) > self._timeout:
            if self._retry_config.reraise:
                raise exc
            raise RetryError(
                f"Time limit {self._retry_config.time_limit} exceeded"
            ) from exc


@overload
def retry_factory(
    func: AwaitableCallable[T],
    retry_config: RetryConfig,
) -> AwaitableCallable[T]:
    ...


@overload
def retry_factory(
    func: RetryCallable[T],
    retry_config: RetryConfig,
) -> RetryCallable[T]:
    ...


def retry_factory(func, retry_config):  # type: ignore
    """
    Function that produces a retry_function given a function to retry,
    and config to determine retry logic.
    """
    retry_hanlder = _RetryHandler(retry_config)
    if asyncio.iscoroutinefunction(func):
        retry_func = _async_retry_factory(func, retry_hanlder)
    else:
        retry_func = _sync_retry_factory(func, retry_hanlder)
    update_wrapper(retry_func, func)
    return retry_func


def _async_retry_factory(
    func: AwaitableCallable[T],
    retry_handler: _RetryHandler,
) -> AwaitableCallable[T]:
    async def retry_func(*args: Any, **kwargs: Any) -> T:
        retry_handler.start()
        while True:
            try:
                return await func(*args, **kwargs)
            except retry_handler.exceptions as exc:
                backoff = retry_handler.handle(exc)
            await asyncio.sleep(backoff)

    return retry_func


def _sync_retry_factory(
    func: RetryCallable[T],
    retry_handler: _RetryHandler,
) -> RetryCallable[T]:
    def retry_func(*args: Any, **kwargs: Any) -> T:
        retry_handler.start()
        while True:
            try:
                return func(*args, **kwargs)
            except retry_handler.exceptions as exc:
                backoff = retry_handler.handle(exc)
            time.sleep(backoff)

    return retry_func
