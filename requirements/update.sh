#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Updating requirements"

docker/run.sh --name requirements_update \
    requirements/inner_update.sh

echo "$(basename "$0") completed successfully!"
