#!/usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

usage()
{
    echo "usage: publish/inner_package.sh REPOSITORY"
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

echo "Building package"
python -m build

echo "Publishing to $REPOSITORY"
twine upload --verbose --repository "$REPOSITORY" dist/*
