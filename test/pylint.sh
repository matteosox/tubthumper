#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running Pylint"

mkdir -p reports

docker/run.sh --name pylint \
    pylint tubthumper test/unit_tests \
    ./*.py version/*.py docs/source/*.py publish/*.py

echo "$(basename "$0") completed successfully!"
