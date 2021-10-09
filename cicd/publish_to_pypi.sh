#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Publishing package"

if ! version/check.sh is_final; then
    echo "Repository set to TestPyPI since this is not a final release"
    REPOSITORY="testpypi"
    export TWINE_PASSWORD="$TESTPYPI_TOKEN"
else
    echo "Repository set to PyPI"
    REPOSITORY="pypi"
    export TWINE_PASSWORD="$PYPI_TOKEN"
fi

export TWINE_USERNAME="__token__"

publish/package.sh $REPOSITORY

echo "$(basename "$0") completed successfully!"
