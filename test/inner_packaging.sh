#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

cleanup() {
    rm -rf dist
}
trap cleanup EXIT

echo "Building package"
python -m build

echo "Checking wheel contents"
check-wheel-contents dist

echo "Checking long description"
twine check dist/*
