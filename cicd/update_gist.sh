#! /usr/bin/env bash
set -euf -o pipefail

# Publishes an update to the badge data Gist

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

docker run \
    --rm \
    --name update_gist \
    --env GIST_TOKEN="$GIST_TOKEN" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    publish/gist.py

echo "All done!"
