#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

echo "Pushing image to Docker Hub for git sha $GIT_SHA"

docker push matteosox/tubthumper-cicd:"$GIT_SHA"
docker tag matteosox/tubthumper-cicd:"$GIT_SHA" matteosox/tubthumper-cicd
docker push matteosox/tubthumper-cicd

echo "$0 completed successfully!"
