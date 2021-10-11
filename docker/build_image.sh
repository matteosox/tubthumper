#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/strict_mode.sh

# Build Docker image

OPTIONS=("--cache-from" "matteosox/tubthumper-cicd")

usage() {
    echo "usage: build_image.sh [--from-scratch -f]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -f | --from-scratch)
            echo "Building from scratch"
            OPTIONS=("--pull" "--no-cache")
            shift 1
            ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            echo "Invalid inputs, see below"
            usage
            exit 1
            ;;
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

echo "$(basename "$0") completed successfully!"
