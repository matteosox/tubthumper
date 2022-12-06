#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Inner shell script for publishing `tubthumper`
# to a Python Package Index

usage() {
    echo "usage: publish/package.sh REPOSITORY"
}

if [[ $# -eq 0 ]]; then
    echo "No repository supplied"
    usage
    exit 2
elif [[ $# -gt 1 ]]; then
    echo "Too many inputs supplied"
    usage
    exit 2
fi

REPOSITORY="$1"

cleanup() {
    rm -rf dist
    rm -rf tubthumper.egg-info
}
trap cleanup EXIT

echo "Building package"
python -m build

echo "Publishing to $REPOSITORY"
twine upload --verbose --repository "$REPOSITORY" dist/*
