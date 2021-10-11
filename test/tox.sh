#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running unit tests with tox"

docker/exec.sh test/inner_tox.sh "$@"

echo "$(basename "$0") completed successfully!"
