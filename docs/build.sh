#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Build documentation

PYLINT_FILE=docs/source/_static/pylint.txt
MYPY_DIR=docs/source/_static/mypy
PYTEST_FILE=docs/source/_static/pytest.html
COVERAGE_DIR=docs/source/_static/coverage

if [[ ! -e "$PYLINT_FILE" ]]; then
    echo "Pylint file $PYLINT_FILE does not exist"
    echo "Generating it by running test/pylint.sh"
    test/pylint.sh
fi

if [[ ! -e "$MYPY_DIR" ]]; then
    echo "Mypy directory $MYPY_DIR does not exist"
    echo "Generating it by running test/mypy.sh"
    test/mypy.sh
fi

if [[ ! -e "$PYTEST_FILE" ]]; then
    echo "Pytest file $PYTEST_FILE does not exist"
    echo "Generating it by running test/unit_tests.sh"
    test/unit_tests.sh
fi

if [[ ! -e "$COVERAGE_DIR" ]]; then
    echo "Coverage directory $COVERAGE_DIR does not exist"
    echo "Generating it by running test/tox.sh"
    test/tox.sh
fi

echo "Building documentation"
docker/exec.sh \
    sphinx-build -T -W -b html docs/source/ docs/build/html

echo "$0 completed successfully!"
