#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Building docs"

LOCAL_GROUP_ID=$(id -g)

docker run \
    --rm \
    --name build_docs \
    --user "1024:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    sphinx-build -W -b html docs/source/ docs/build/html
