#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running unit tests"
docker/exec.sh python -m pytest --html=docs/source/_static/pytest.html --self-contained-html

echo "$0 completed successfully!"
