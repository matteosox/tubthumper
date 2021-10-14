#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Testing documentation"

docs/build.sh

echo "Running doctest"
docker/exec.sh \
    sphinx-build -T -W -b doctest docs/source/ docs/build/html

echo "$0 completed successfully!"
