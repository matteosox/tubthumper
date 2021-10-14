#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running Pylint"

docker/exec.sh pylint tubthumper test/unit_tests \
    ./*.py docs/**/*.py publish/*.py

echo "$0 completed successfully!"
