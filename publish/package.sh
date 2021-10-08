#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

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

echo "Publishing package to $REPOSITORY"

docker run \
    --rm \
    --name publish_package \
    --env TWINE_USERNAME="$TWINE_USERNAME" \
    --env TWINE_PASSWORD="$TWINE_PASSWORD" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    publish/inner_package.sh "$REPOSITORY"
