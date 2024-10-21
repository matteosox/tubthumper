#!/usr/bin/env python3

import os

from github import Auth, Github
from packaging.version import Version

import tubthumper


def main() -> None:
    auth = Auth.Token(os.environ["GITHUB_TOKEN"])
    github = Github(auth=auth)
    repo = github.get_repo("matteosox/tubthumper")
    tag = f"f{tubthumper.__version__}"
    name = tubthumper.__version__
    prerelease = Version(tubthumper.__version__).is_prerelease
    repo.create_git_release(
        tag=tag,
        name=name,
        draft=True,
        prerelease=prerelease,
    )


if __name__ == "__main__":
    main()
