#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Building docs"

if ! cp -R reports docs/source/_static; then
    echo "reports directory not found"
    echo "Generating it by running test suite"
    cicd/test.sh
fi

docker/exec.sh \
    sphinx-build -W -b html docs/source/ docs/build/html

echo "$(basename "$0") completed successfully!"
