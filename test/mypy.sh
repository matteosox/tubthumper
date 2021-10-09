#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running Mypy"

docker/exec.sh mypy --package tubthumper

echo "$(basename "$0") completed successfully!"
