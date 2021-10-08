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

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)

docker run \
    --rm \
    --name publish_package \
    --env TWINE_USERNAME="$TWINE_USERNAME" \
    --env TWINE_PASSWORD="$TWINE_PASSWORD" \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    publish/inner_package.sh "$REPOSITORY"
