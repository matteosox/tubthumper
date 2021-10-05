#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Checking version"

docker run \
    --rm \
    --name version_check \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    python -m version.inner_check "$@"
