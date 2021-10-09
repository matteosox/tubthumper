#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

# Publishes tag to Github for prereleases and final releases

docker/run.sh --env GITHUB_TOKEN --name tag \
    publish/tag.py

echo "$(basename "$0") completed successfully!"
