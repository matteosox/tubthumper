"""Interfaces for tubthumper package"""

import logging
from typing import Callable

from tubthumper import _types
from tubthumper._retry_factory import RetryConfig
from tubthumper._retry_factory import retry_factory as _retry_factory

__all__ = ["retry", "retry_decorator", "retry_factory"]

RETRY_LIMIT_DEFAULT = float("inf")
TIME_LIMIT_DEFAULT = float("inf")
INIT_BACKOFF_DEFAULT = 1
EXPONENTIAL_DEFAULT = 2
JITTER_DEFAULT = True
RERAISE_DEFAULT = False
LOG_LEVEL_DEFAULT = logging.WARNING
LOGGER_DEFAULT = logging.getLogger("tubthumper")


def retry(
    call_able: Callable[..., _types.ReturnType],
    *,
    exceptions: _types.ExceptionsType,
    args: _types.ArgsType = None,
    kwargs: _types.KwargsType = None,
    retry_limit: _types.RetryLimitType = RETRY_LIMIT_DEFAULT,
    time_limit: _types.TimeLimitType = TIME_LIMIT_DEFAULT,
    init_backoff: _types.InitBackoffType = INIT_BACKOFF_DEFAULT,
    exponential: _types.ExponentialType = EXPONENTIAL_DEFAULT,
    jitter: _types.JitterType = JITTER_DEFAULT,
    reraise: _types.ReraiseType = RERAISE_DEFAULT,
    log_level: _types.LogLevelType = LOG_LEVEL_DEFAULT,
    logger: _types.LoggerType = LOGGER_DEFAULT,
) -> _types.ReturnType:
    r"""
    Call the provided callable with retry logic.

    :param call_able:
        the callable to be called
    :param exceptions:
        the exceptions to be caught for retry
    :param args:
        positional arguments for the callable
    :param kwargs:
        keyword arguments for the callable
    :param retry_limit:
        the number of retries to perform before not catching
        the given exceptions
    :param time_limit:
        the maximum number of seconds after the callable is called
        for a retry attempt to begin
    :param init_backoff:
        the number of seconds to sleep for the first retry
    :param exponential:
        time between retries grows by ``exponential ** n``
    :param jitter:
        whether or not to "jitter" the exponential backoff randomly
    :param reraise:
        whether or not to re-raise the caught exception instead of
        a RetryError when a retry or time limit is reached
    :param log_level:
        the level for logging of caught exceptions
    :param logger:
        the logger to log caught exceptions with

    :returns:
        the returned object of the callable
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    retry_config = RetryConfig(
        exceptions=exceptions,
        retry_limit=retry_limit,
        time_limit=time_limit,
        init_backoff=init_backoff,
        exponential=exponential,
        jitter=jitter,
        reraise=reraise,
        log_level=log_level,
        logger=logger,
    )
    retry_func = _retry_factory(call_able, retry_config)
    return retry_func(*args, **kwargs)


def retry_decorator(
    *,
    exceptions: _types.ExceptionsType,
    retry_limit: _types.RetryLimitType = RETRY_LIMIT_DEFAULT,
    time_limit: _types.TimeLimitType = TIME_LIMIT_DEFAULT,
    init_backoff: _types.InitBackoffType = INIT_BACKOFF_DEFAULT,
    exponential: _types.ExponentialType = EXPONENTIAL_DEFAULT,
    jitter: _types.JitterType = JITTER_DEFAULT,
    reraise: _types.ReraiseType = RERAISE_DEFAULT,
    log_level: _types.LogLevelType = LOG_LEVEL_DEFAULT,
    logger: _types.LoggerType = LOGGER_DEFAULT,
) -> Callable[[Callable[..., _types.ReturnType]], Callable[..., _types.ReturnType]]:
    r"""
    Construct a decorator function for defining a function with built-in retry logic.

    :param exceptions:
        the exceptions to be caught for retry
    :param retry_limit:
        the number of retries to perform before not catching
        the given exceptions
    :param time_limit:
        the maximum number of seconds after the callable is called
        for a retry attempt to begin
    :param init_backoff:
        the number of seconds to sleep for the first retry
    :param exponential:
        time between retries grows by ``exponential ** n``
    :param jitter:
        whether or not to "jitter" the exponential backoff randomly
    :param reraise:
        whether or not to re-raise the caught exception instead of
        a RetryError when a retry or time limit is reached
    :param log_level:
        the level for logging of caught exceptions
    :param logger:
        the logger to log caught exceptions with
    :returns:
        a decorator function that, when used as such,
        returns a function that looks like the callable it
        decorates, but with configured retry logic
    """

    def decorator(
        call_able: Callable[..., _types.ReturnType],
    ) -> Callable[..., _types.ReturnType]:
        retry_config = RetryConfig(
            exceptions=exceptions,
            retry_limit=retry_limit,
            time_limit=time_limit,
            init_backoff=init_backoff,
            exponential=exponential,
            jitter=jitter,
            reraise=reraise,
            log_level=log_level,
            logger=logger,
        )
        return _retry_factory(call_able, retry_config)

    return decorator


def retry_factory(
    call_able: Callable[..., _types.ReturnType],
    *,
    exceptions: _types.ExceptionsType,
    retry_limit: _types.RetryLimitType = RETRY_LIMIT_DEFAULT,
    time_limit: _types.TimeLimitType = TIME_LIMIT_DEFAULT,
    init_backoff: _types.InitBackoffType = INIT_BACKOFF_DEFAULT,
    exponential: _types.ExponentialType = EXPONENTIAL_DEFAULT,
    jitter: _types.JitterType = JITTER_DEFAULT,
    reraise: _types.ReraiseType = RERAISE_DEFAULT,
    log_level: _types.LogLevelType = LOG_LEVEL_DEFAULT,
    logger: _types.LoggerType = LOGGER_DEFAULT,
) -> Callable[..., _types.ReturnType]:
    r"""
    Construct a function with built-in retry logic given a callable to retry.

    :param call_able:
        the callable to be called
    :param exceptions:
        the exceptions to be caught for retry
    :param retry_limit:
        the number of retries to perform before not catching
        the given exceptions
    :param time_limit:
        the maximum number of seconds after the callable is called
        for a retry attempt to begin
    :param init_backoff:
        the number of seconds to sleep for the first retry
    :param exponential:
        time between retries grows by ``exponential ** n``
    :param jitter:
        whether or not to "jitter" the exponential backoff randomly
    :param reraise:
        whether or not to re-raise the caught exception instead of
        a RetryError when a retry or time limit is reached
    :param log_level:
        the level for logging of caught exceptions
    :param logger:
        the logger to log caught exceptions with
    :returns:
        a function that looks like the callable it decorates,
        but with configured retry logic
    """
    retry_config = RetryConfig(
        exceptions=exceptions,
        retry_limit=retry_limit,
        time_limit=time_limit,
        init_backoff=init_backoff,
        exponential=exponential,
        jitter=jitter,
        reraise=reraise,
        log_level=log_level,
        logger=logger,
    )
    return _retry_factory(call_able, retry_config)
