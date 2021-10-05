#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

GIT_SHA=$(git rev-parse --short HEAD)
echo "Building & tagging cicd Docker image for git sha $GIT_SHA"

export DOCKER_BUILDKIT=1

docker build \
    --progress=plain \
    --tag matteosox/tubthumper-cicd:"$GIT_SHA" \
    --cache-from matteosox/tubthumper-cicd \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --file cicd/Dockerfile \
    .

docker tag matteosox/tubthumper-cicd:"$GIT_SHA" matteosox/tubthumper-cicd

echo "All done!"
