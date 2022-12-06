"""Interfaces for tubthumper package"""

import logging
from typing import Callable

from tubthumper import _types as tub_types
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
    func: Callable[tub_types.P, tub_types.T],
    *,
    exceptions: tub_types.Exceptions,
    args: tub_types.Args = None,
    kwargs: tub_types.Kwargs = None,
    retry_limit: tub_types.RetryLimit = RETRY_LIMIT_DEFAULT,
    time_limit: tub_types.Duration = TIME_LIMIT_DEFAULT,
    init_backoff: tub_types.Duration = INIT_BACKOFF_DEFAULT,
    exponential: tub_types.Exponential = EXPONENTIAL_DEFAULT,
    jitter: tub_types.Jitter = JITTER_DEFAULT,
    reraise: tub_types.Reraise = RERAISE_DEFAULT,
    log_level: tub_types.LogLevel = LOG_LEVEL_DEFAULT,
    logger: tub_types.Logger = LOGGER_DEFAULT,
) -> tub_types.T:
    r"""Call the provided callable with retry logic.

    For usage examples, see `here <index.html#usage>`__.

    Args:
        func:
            callable to be called
        exceptions:
            exceptions to be caught, resulting in a retry
        args:
            positional arguments for the callable
        kwargs:
            keyword arguments for the callable
        retry_limit:
            number of retries to perform before raising an exception,
            e.g. ``retry_limit=1`` results in at most two calls
        time_limit:
            duration in seconds after which a retry attempt will
            be prevented by raising an exception, i.e. not a timeout
            stopping long running calls, but rather a mechanism to prevent
            retry attempts after a certain duration
        init_backoff:
            duration in seconds to sleep before the first retry
        exponential:
            backoff duration between retries grows by this factor with each retry
        jitter:
            whether or not to "jitter" the backoff duration randomly
        reraise:
            whether or not to re-raise the caught exception instead of
            a `RetryError` when a retry or time limit is reached
        log_level:
            level for logging caught exceptions, defaults to `logging.WARNING`
        logger:
            logger to log caught exceptions with

    Raises:
        RetryError:
            Raised when a retry or time limit is reached, unless ``reraise=True``

    Returns:
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
    retry_func = _retry_factory(func, retry_config)
    return retry_func(*args, **kwargs)


def retry_decorator(
    *,
    exceptions: tub_types.Exceptions,
    retry_limit: tub_types.RetryLimit = RETRY_LIMIT_DEFAULT,
    time_limit: tub_types.Duration = TIME_LIMIT_DEFAULT,
    init_backoff: tub_types.Duration = INIT_BACKOFF_DEFAULT,
    exponential: tub_types.Exponential = EXPONENTIAL_DEFAULT,
    jitter: tub_types.Jitter = JITTER_DEFAULT,
    reraise: tub_types.Reraise = RERAISE_DEFAULT,
    log_level: tub_types.LogLevel = LOG_LEVEL_DEFAULT,
    logger: tub_types.Logger = LOGGER_DEFAULT,
) -> Callable[[Callable[tub_types.P, tub_types.T]], Callable[tub_types.P, tub_types.T]]:
    r"""Construct a decorator function for defining a function with built-in retry logic.

    For usage examples, see `here <index.html#usage>`__.

    Args:
        exceptions:
            exceptions to be caught, resulting in a retry
        retry_limit:
            number of retries to perform before raising an exception,
            e.g. ``retry_limit=1`` results in at most two calls
        time_limit:
            duration in seconds after which a retry attempt will
            be prevented by raising an exception, i.e. not a timeout
            stopping long running calls, but rather a mechanism to prevent
            retry attempts after a certain duration
        init_backoff:
            duration in seconds to sleep before the first retry
        exponential:
            backoff duration between retries grows by this factor with each retry
        jitter:
            whether or not to "jitter" the backoff duration randomly
        reraise:
            whether or not to re-raise the caught exception instead of
            a `RetryError` when a retry or time limit is reached
        log_level:
            level for logging caught exceptions, defaults to `logging.WARNING`
        logger:
            logger to log caught exceptions with

    Raises:
        RetryError:
            Raised when a retry or time limit is reached, unless ``reraise=True``

    Returns:
        a decorator function that, when used as such,
        returns a function that looks like the callable it
        decorates, but with configured retry logic
    """

    def decorator(
        func: Callable[tub_types.P, tub_types.T]
    ) -> Callable[tub_types.P, tub_types.T]:
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
        return _retry_factory(func, retry_config)

    return decorator


def retry_factory(
    func: Callable[tub_types.P, tub_types.T],
    *,
    exceptions: tub_types.Exceptions,
    retry_limit: tub_types.RetryLimit = RETRY_LIMIT_DEFAULT,
    time_limit: tub_types.Duration = TIME_LIMIT_DEFAULT,
    init_backoff: tub_types.Duration = INIT_BACKOFF_DEFAULT,
    exponential: tub_types.Exponential = EXPONENTIAL_DEFAULT,
    jitter: tub_types.Jitter = JITTER_DEFAULT,
    reraise: tub_types.Reraise = RERAISE_DEFAULT,
    log_level: tub_types.LogLevel = LOG_LEVEL_DEFAULT,
    logger: tub_types.Logger = LOGGER_DEFAULT,
) -> Callable[tub_types.P, tub_types.T]:
    r"""Construct a function with built-in retry logic given a callable to retry.

    For usage examples, see `here <index.html#usage>`__.

    Args:
        func:
            callable to be called
        exceptions:
            exceptions to be caught, resulting in a retry
        retry_limit:
            number of retries to perform before raising an exception,
            e.g. ``retry_limit=1`` results in at most two calls
        time_limit:
            duration in seconds after which a retry attempt will
            be prevented by raising an exception, i.e. not a timeout
            stopping long running calls, but rather a mechanism to prevent
            retry attempts after a certain duration
        init_backoff:
            duration in seconds to sleep before the first retry
        exponential:
            backoff duration between retries grows by this factor with each retry
        jitter:
            whether or not to "jitter" the backoff duration randomly
        reraise:
            whether or not to re-raise the caught exception instead of
            a `RetryError` when a retry or time limit is reached
        log_level:
            level for logging caught exceptions, defaults to `logging.WARNING`
        logger:
            logger to log caught exceptions with

    Raises:
        RetryError:
            Raised when a retry or time limit is reached, unless ``reraise=True``

    Returns:
        a function that looks like the callable provided,
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
    return _retry_factory(func, retry_config)
