#!/usr/bin/env python3
"""Python script for updating the badge data Gist"""

import inspect
import json
import logging
import os
import pprint
import re
from typing import Any

import requests

from tubthumper import __version__ as version
from tubthumper import retry_decorator

logger = logging.getLogger(__name__)


def main() -> None:
    """Updates the badge data Gist"""
    _configure_logger()
    mypy_score = _get_mypy_score()
    logger.info(f"MyPy score: {mypy_score}")

    pylint_score = _get_pylint_score()
    logger.info(f"Pylint score: {pylint_score}")

    mypy_badge_data = _get_mypy_badge_data(mypy_score)
    logger.info(f"MyPy badge data:\n{mypy_badge_data}")

    pylint_badge_data = _get_pylint_badge_data(pylint_score)
    logger.info(f"Pylint badge data:\n{pylint_badge_data}")

    auth = ("token", os.environ["GIST_TOKEN"])
    headers = {"accept": "application/vnd.github.v3+json"}
    data = {
        "files": {
            "mypy.json": {"content": mypy_badge_data},
            "pylint.json": {"content": pylint_badge_data},
        },
        "description": f"Updated Badge Data for tubthumper=={version}",
    }
    response = _request_with_retry(
        "PATCH",
        "https://api.github.com/gists/bd79bbd912687bf44fac6b7887d18f14",
        headers=headers,
        auth=auth,
        json=data,
    )
    response.raise_for_status()
    logger.info(f"Github Response:\n{pprint.pformat(response.json())}")


def _configure_logger(level: int = logging.INFO) -> None:
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


def _dir_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def _get_mypy_score() -> float:
    summary_line = '<th class="summary summary-filename">Total</th>'
    report_path = os.path.join(_dir_path(), "..", "reports", "mypy", "index.html")
    with open(report_path, encoding="utf-8") as report_file:
        while not (line := report_file.readline()).startswith(summary_line):
            pass
        line = report_file.readline()
    match = re.match(
        r'<th class="summary summary-precision">(\d{0,2}\.\d{2})% imprecise</th>', line
    )
    return 100 - float(match.group(1))


def _get_pylint_score() -> float:
    report_path = os.path.join(_dir_path(), "..", "reports", "pylint.txt")
    with open(report_path, encoding="utf-8") as report_file:
        report_lines = report_file.readlines()
    match = re.match(r"Your code has been rated at (\d{2}\.\d{2})/10", report_lines[-2])
    return float(match.group(1))


def _get_mypy_badge_data(score: float) -> str:
    message = f"{score:.2f}%"
    hue = round(1.2 * score)
    return _generate_badge_data(label="MyPy", message=message, hue=hue)


def _get_pylint_badge_data(score: float) -> str:
    message = f"{score:.2f}/10"
    hue = round(6 * score) + (60 if score == 10 else 0)
    return _generate_badge_data(label="Pylint", message=message, hue=hue)


def _generate_badge_data(label: str, message: str, hue: int) -> str:
    return json.dumps(
        {
            "schemaVersion": 1,
            "label": label,
            "message": message,
            "color": f"hsl({hue}, 80%, 50%)",
        },
        indent=2,
    )


@retry_decorator(
    exceptions=(requests.Timeout, requests.ConnectionError, requests.HTTPError)
)
def _request_with_retry(*args: Any, **kwargs: Any) -> requests.models.Response:
    response = requests.request(*args, **kwargs)
    if 500 <= response.status_code < 600:
        response.raise_for_status()
    return response


if __name__ == "__main__":
    __file__ = inspect.getsourcefile(lambda: 0)
    main()
