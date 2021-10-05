#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Running Pylint"

mkdir -p reports

docker run \
    --rm \
    --name pylint \
    --env PYLINTHOME=/home/cicd/tubthumper \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    pylint tubthumper test/unit_tests version/inner_check.py docs/source/conf.py publish/tag.py
