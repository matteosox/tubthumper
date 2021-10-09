#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running Pylint"

mkdir -p reports

docker/run.sh --name pylint \
    pylint tubthumper test/unit_tests util.py version/inner_check.py docs/source/conf.py publish/tag.py publish/gist.py

echo "$(basename "$0") completed successfully!"
