#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

echo "Setting up Docker"

echo "Pulling latest image"
docker pull matteosox/tubthumper-cicd

docker/build.sh

echo "$(basename "$0") completed successfully!"
