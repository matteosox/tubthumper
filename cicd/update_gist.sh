#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

echo "Updating the badge data Gist"

PYLINT_FILE=docs/source/_static/pylint.txt
MYPY_FILE=docs/source/_static/mypy/index.html

if [[ ! -e "$PYLINT_FILE" ]]; then
    echo "Pylint file $PYLINT_FILE does not exist"
    echo "Generating it by running test/pylint.sh"
    test/pylint.sh
fi

if [[ ! -e "$MYPY_FILE" ]]; then
    echo "MyPy file $MYPY_FILE does not exist"
    echo "Generating it by running test/mypy.sh"
    test/mypy.sh
fi

docker/exec.sh --env GIST_TOKEN \
    publish/gist.py

echo "$(basename "$0") completed successfully!"
