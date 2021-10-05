#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Running Mypy"

LOCAL_GROUP_ID=$(id -g)

docker run \
    --rm \
    --name mypy \
    --user "1024:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    mypy --package tubthumper
