"""Module defining the retry_factory function"""

import asyncio
import random
import time
from dataclasses import dataclass
from functools import update_wrapper
from typing import Awaitable, Callable, overload

from tubthumper import _types as tub_types


class RetryError(Exception):
    """Exception raised when a retry or time limit is reached"""


@dataclass(frozen=True)
class RetryConfig:
    """Config class for retry logic"""

    exceptions: tub_types.Exceptions
    retry_limit: tub_types.RetryLimit
    time_limit: tub_types.Duration
    init_backoff: tub_types.Duration
    exponential: tub_types.Exponential
    jitter: tub_types.Jitter
    reraise: tub_types.Reraise
    log_level: tub_types.LogLevel
    logger: tub_types.Logger


class _RetryHandler:
    """Class for handling exceptions to be retried"""

    exceptions: tub_types.Exceptions
    _retry_config: RetryConfig
    _timeout: tub_types.Duration
    _count: int
    _backoff: tub_types.Duration
    _unjittered_backoff: tub_types.Duration

    def __init__(self, retry_config: RetryConfig):
        self.exceptions = retry_config.exceptions
        self._retry_config = retry_config

        self._calc_backoff: Callable[[], tub_types.Duration]
        if self._retry_config.jitter:
            self._calc_backoff = lambda: self._unjittered_backoff * random.random()
        else:
            self._calc_backoff = lambda: self._unjittered_backoff

    def start(self) -> None:
        """Initialize the retry handler's timeout, count, and backoff"""
        self._timeout = time.perf_counter() + self._retry_config.time_limit
        self._count = 0
        self._unjittered_backoff = self._retry_config.init_backoff

    def handle(self, exc: Exception) -> tub_types.Duration:
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
    func: Callable[tub_types.P, Awaitable[tub_types.T]],
    retry_config: RetryConfig,
) -> Callable[tub_types.P, Awaitable[tub_types.T]]: ...


@overload
def retry_factory(
    func: Callable[tub_types.P, tub_types.T],
    retry_config: RetryConfig,
) -> Callable[tub_types.P, tub_types.T]: ...


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
    func: Callable[tub_types.P, Awaitable[tub_types.T]],
    retry_handler: _RetryHandler,
) -> Callable[tub_types.P, Awaitable[tub_types.T]]:
    async def retry_func(
        *args: tub_types.P.args, **kwargs: tub_types.P.kwargs
    ) -> tub_types.T:
        retry_handler.start()
        while True:
            try:
                return await func(*args, **kwargs)
            except retry_handler.exceptions as exc:
                backoff = retry_handler.handle(exc)
            await asyncio.sleep(backoff)

    return retry_func


def _sync_retry_factory(
    func: Callable[tub_types.P, tub_types.T],
    retry_handler: _RetryHandler,
) -> Callable[tub_types.P, tub_types.T]:
    def retry_func(
        *args: tub_types.P.args, **kwargs: tub_types.P.kwargs
    ) -> tub_types.T:
        retry_handler.start()
        while True:
            try:
                return func(*args, **kwargs)
            except retry_handler.exceptions as exc:
                backoff = retry_handler.handle(exc)
            time.sleep(backoff)

    return retry_func
