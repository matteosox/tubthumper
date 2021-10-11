#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/strict_mode.sh

# Create Docker container

CONTAINER_NAME="tubthumper-cicd-$GIT_SHA"
IMAGE_REF="matteosox/tubthumper-cicd:$GIT_SHA"

docker rm -f "$CONTAINER_NAME" &> /dev/null || true

IMAGES=$(docker images --filter=reference="$IMAGE_REF" --format "{{.Repository}}:{{.Tag}}")

if [[ -z "$IMAGES" ]]; then
    echo "No $IMAGE_REF Docker image found, so creating it for you"
    docker/build_image.sh
fi

echo "Creating new Docker container"
docker run \
    --detach \
    --name "$CONTAINER_NAME" \
    --volume "$REPO_DIR":/root/tubthumper \
    "$IMAGE_REF"

echo "$(basename "$0") completed successfully!"
