"""Python module with single public download_reports function"""

import io
import logging
import os
import shlex
import subprocess
import zipfile
from typing import Tuple

import tubthumper
from util import configure_logger, request_with_retry

logger = configure_logger(logging.getLogger(__name__))

GITHUB_HEADERS = {"accept": "application/vnd.github.v3+json"}
PER_PAGE = 100
ARTIFACTS_URL = "https://api.github.com/repos/matteosox/tubthumper/actions/artifacts"
GET = "GET"


def download_reports() -> None:
    """Downloads reports artifact from Github for corresponding git sha"""
    logger.info("Getting reports from Github")
    git_sha = _get_git_sha()
    logger.info(f"Determining artifacts id for git sha {git_sha}")
    artifact_id = _get_reports_artifact_id(git_sha)
    logger.info(f"Downloading artifact with id {artifact_id}")
    _download_artfact(artifact_id)


def _get_git_sha() -> str:
    completed_process = subprocess.run(
        shlex.split("git rev-parse --short HEAD"),
        check=True,
        text=True,
        capture_output=True,
    )
    return completed_process.stdout.strip()


class ArtifactNotFoundError(Exception):
    """Thrown when an artifact can't be found"""


@tubthumper.retry_decorator(
    exceptions=ArtifactNotFoundError, exponential=1, init_backoff=30, jitter=False
)
def _get_reports_artifact_id(git_sha: str) -> int:
    auth = _get_auth_header()
    name = f"reports_{git_sha}"
    page = 1
    while True:
        params = {"page": page, "per_page": PER_PAGE}
        response = request_with_retry(
            GET,
            ARTIFACTS_URL,
            headers=GITHUB_HEADERS,
            params=params,
            auth=auth,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        for artifact in result["artifacts"]:
            if artifact["name"] == name:
                return artifact["id"]
        if result["total_count"] < PER_PAGE:
            raise ArtifactNotFoundError(
                f"Could not find reports artifact for git_sha {git_sha}"
            )
        page += 1


def _get_auth_header() -> Tuple[str, str]:
    return ("token", os.environ["GITHUB_TOKEN"])


def _download_artfact(artifact_id: int) -> None:
    auth = _get_auth_header()
    response = request_with_retry(
        GET,
        f"{ARTIFACTS_URL}/{artifact_id}/zip",
        headers=GITHUB_HEADERS,
        auth=auth,
        timeout=10,
    )
    response.raise_for_status()
    destination = os.path.join(_dir_path(), "_static", "reports")
    with zipfile.ZipFile(io.BytesIO(response.content)) as myzip:
        myzip.extractall(path=destination)


def _dir_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))
