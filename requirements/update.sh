#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Updating requirements/requirements.txt"

docker run \
    --rm \
    --name requirements_update \
    --volume "$REPO_DIR"/requirements:/home/cicd/tubthumper/requirements \
    matteosox/tubthumper-cicd \
    requirements/inner_update.sh
