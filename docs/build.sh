#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Building docs"


if ! cp -R reports docs/source/_static; then
    echo "reports directory not found"
    echo "Generating it by running test suite"
    cicd/test.sh
fi

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)

docker run \
    --rm \
    --name build_docs \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    sphinx-build -W -b html docs/source/ docs/build/html
