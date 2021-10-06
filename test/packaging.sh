#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Testing packaging"

LOCAL_USER_ID=$(id --user)
LOCAL_GROUP_ID=$(id --group)

docker run \
    --rm \
    --name test_packaging \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    test/inner_packaging.sh
