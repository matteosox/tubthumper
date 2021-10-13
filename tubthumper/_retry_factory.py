"""Module defining the retry_factory function"""

import asyncio
import itertools
import random
import time
from dataclasses import dataclass
from functools import update_wrapper
from typing import Any, overload

from tubthumper import _types
from tubthumper._types import AwaitableCallable, RetryCallable, T

__all__ = ["RetryError"]

COUNTER_EXCEPTION = RuntimeError("Infinite retry counter stopped iteration")


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
    if asyncio.iscoroutinefunction(func):
        retry_func = _async_retry_factory(func, retry_config)
    else:
        retry_func = _sync_retry_factory(func, retry_config)
    update_wrapper(retry_func, func)
    return retry_func


def _async_retry_factory(
    func: AwaitableCallable[T],
    retry_config: RetryConfig,
) -> AwaitableCallable[T]:
    async def retry_func(*args: Any, **kwargs: Any) -> T:
        retry_timeout = _get_timeout(retry_config.time_limit)
        for retry_count in itertools.count():
            try:
                return await func(*args, **kwargs)
            except retry_config.exceptions as exc:
                backoff = _process_exception(
                    retry_config, exc, retry_count, retry_timeout
                )
            await asyncio.sleep(backoff)
        raise COUNTER_EXCEPTION

    return retry_func


def _sync_retry_factory(
    func: RetryCallable[T],
    retry_config: RetryConfig,
) -> RetryCallable[T]:
    def retry_func(*args: Any, **kwargs: Any) -> T:
        retry_timeout = _get_timeout(retry_config.time_limit)
        for retry_count in itertools.count():
            try:
                return func(*args, **kwargs)
            except retry_config.exceptions as exc:
                backoff = _process_exception(
                    retry_config, exc, retry_count, retry_timeout
                )
            time.sleep(backoff)
        raise COUNTER_EXCEPTION

    return retry_func


def _process_exception(
    retry_config: RetryConfig, exc: Exception, retry_count: int, retry_timeout: float
) -> float:
    if retry_count >= retry_config.retry_limit:
        if retry_config.reraise:
            raise exc
        raise RetryError(f"Retry limit {retry_config.retry_limit} reached") from exc
    backoff = retry_config.init_backoff * retry_config.exponential ** retry_count
    if retry_config.jitter:
        backoff *= random.random()
    if (time.perf_counter() + backoff) > retry_timeout:
        if retry_config.reraise:
            raise exc
        raise RetryError(f"Time limit {retry_config.time_limit} exceeded") from exc
    retry_config.logger.log(
        retry_config.log_level,
        f"Function threw exception below on try {retry_count + 1}, "
        f"retrying in {backoff:.3f} seconds",
        exc_info=True,
    )
    return backoff


def _get_timeout(time_limit: _types.TimeLimit) -> float:
    return time.perf_counter() + time_limit
