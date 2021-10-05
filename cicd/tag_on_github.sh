#! /usr/bin/env bash
set -euf -o pipefail

# Publishes tag to Github for prereleases and final releases

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

docker run \
    --rm \
    --name tag \
    --env GITHUB_TOKEN="$GITHUB_TOKEN" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    publish/tag.py

echo "All done!"
