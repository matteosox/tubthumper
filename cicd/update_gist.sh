#! /usr/bin/env bash
set -euf -o pipefail

# Publishes an update to the badge data Gist

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

PYLINT_FILE="$REPO_DIR/reports/pylint.txt"
MYPY_FILE="$REPO_DIR/reports/mypy/index.html"

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

docker run \
    --rm \
    --name update_gist \
    --env GIST_TOKEN="$GIST_TOKEN" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    publish/gist.py

echo "All done!"
