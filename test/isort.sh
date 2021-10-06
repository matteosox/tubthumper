#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Running isort"

LOCAL_USER_ID=$(id --user)
LOCAL_GROUP_ID=$(id --group)

if ! docker run \
    --rm \
    --name isort \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    isort . "$@"; then
    echo "isort check failed. Run test/isort.sh to resolve."
    exit 1
fi
