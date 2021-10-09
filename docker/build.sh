#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/strict_mode.sh

echo "Building & tagging cicd Docker image"

OPTIONS=("--progress=plain")

usage()
{
    echo "usage: build.sh [--from-scratch -f]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -f | --from-scratch )
            OPTIONS+=("--pull" "--no-cache")
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

docker build \
    "${OPTIONS[@]}" \
    --tag matteosox/tubthumper-cicd:"$GIT_SHA" \
    --file docker/Dockerfile \
    .

docker tag matteosox/tubthumper-cicd:"$GIT_SHA" matteosox/tubthumper-cicd

echo "$(basename "$0") completed successfully!"
