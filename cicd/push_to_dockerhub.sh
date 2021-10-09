#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

echo "Pushing image to Docker Hub for git sha $GIT_SHA"

docker push matteosox/tubthumper-cicd:"$GIT_SHA"
docker push matteosox/tubthumper-cicd

echo "$(basename "$0") completed successfully!"
