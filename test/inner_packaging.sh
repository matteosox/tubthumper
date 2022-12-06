#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Inner shell script for testing packaging

cleanup() {
    rm -rf dist
    rm -rf tubthumper.egg-info
}
trap cleanup EXIT

echo "Building package"
python -m build

echo "Checking wheel contents"
check-wheel-contents dist

echo "Checking long description"
twine check dist/*
