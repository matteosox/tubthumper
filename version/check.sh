#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Checking version"

docker/run.sh --name version_check \
    version/inner_check.py "$@"
