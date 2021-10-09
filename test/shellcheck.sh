#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Running ShellCheck"

docker/run.sh --name shellcheck \
    test/inner_shellcheck.sh

echo "$(basename "$0") completed successfully!"
