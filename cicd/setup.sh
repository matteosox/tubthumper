#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

# Build & tag Docker image, create Docker container

OPTIONS=("--cache-from" "matteosox/tubthumper-cicd")

usage()
{
    echo "usage: setup.sh [--from-scratch -f]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -f | --from-scratch )
            echo "Building from scratch"
            OPTIONS=("--pull" "--no-cache")
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            echo "Invalid inputs, see below"
            usage
            exit 1
    esac
done

export DOCKER_BUILDKIT=1
echo "Building Docker image"
docker build \
    "${OPTIONS[@]}" \
    --progress=plain \
    --tag matteosox/tubthumper-cicd:"$GIT_SHA" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --file docker/Dockerfile \
    .

echo "Tagging Docker image"
docker tag matteosox/tubthumper-cicd:"$GIT_SHA" matteosox/tubthumper-cicd

echo "Removing previous Docker container"
NAME="tubthumper-cicd"
docker rm -f "$NAME" &> /dev/null || true

echo "Creating new Docker container"
LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)
docker run \
    --detach \
    --name "$NAME" \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd

echo "$(basename "$0") completed successfully!"
