#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

if ! version/check.sh is_final; then
    echo "Publishing package to TestPyPI since this is not a final release"
    REPOSITORY="testpypi"
    export TWINE_PASSWORD="$TESTPYPI_TOKEN"
else
    echo "Publishing package to PyPI"
    REPOSITORY="pypi"
    export TWINE_PASSWORD="$PYPI_TOKEN"
fi

export TWINE_USERNAME="__token__"

publish/package.sh $REPOSITORY

echo "All done!"
