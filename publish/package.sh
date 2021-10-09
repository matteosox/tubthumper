#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Publishing package"

usage()
{
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
else
    REPOSITORY="$1"
fi

echo "Repository set to $REPOSITORY"

docker/exec.sh --env TWINE_USERNAME --env TWINE_PASSWORD \
    publish/inner_package.sh "$REPOSITORY"

echo "$(basename "$0") completed successfully!"
