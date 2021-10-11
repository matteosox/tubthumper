#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running unit tests"
docker/exec.sh test/inner_unit_tests.sh --no-coverage

echo "$(basename "$0") completed successfully!"
