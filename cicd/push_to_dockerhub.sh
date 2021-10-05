#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

GIT_SHA=$(git rev-parse --short HEAD)
echo "Pushing image to Docker Hub for git sha $GIT_SHA"

docker push matteosox/tubthumper-cicd:"$GIT_SHA"
docker push matteosox/tubthumper-cicd

echo "All done!"
