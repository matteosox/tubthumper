"""Repo-wide Python utilities"""

import logging
from typing import Any, TypeVar

import requests

from tubthumper import retry_decorator

LoggerType = TypeVar("LoggerType", bound=logging.Logger)


def configure_logger(logger: LoggerType, level: int = logging.INFO) -> LoggerType:
    """
    Configures logger with a nice formatter,
    with optional level, defaulting to info
    """
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s | %(pathname)s:%(funcName)s "
        "@ %(lineno)d | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %Z",
    )
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


@retry_decorator(
    exceptions=(requests.Timeout, requests.ConnectionError, requests.HTTPError)
)
def request_with_retry(
    method: str, url: str, **kwargs: Any
) -> requests.models.Response:
    """
    Wrapper function for `requests.request` that retries
    timeout, connection, and server-side http errors with
    exponential backoff and jitter. For more info:
    https://docs.python-requests.org/en/latest/api/#requests.request
    """
    response = requests.request(method, url, **kwargs)
    if 500 <= response.status_code < 600:
        response.raise_for_status()
    return response
