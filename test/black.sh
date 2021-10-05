#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Running Black"

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)

if ! docker run \
    --rm \
    --name black \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    black "$@" .; then
    echo "black check failed. Run test/black.sh to resolve."
    exit 1
fi
