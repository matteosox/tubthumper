#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Running Mypy"

LOCAL_USER_ID=$(id --user)
LOCAL_GROUP_ID=$(id --group)

docker run \
    --rm \
    --name mypy \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    mypy --package tubthumper
