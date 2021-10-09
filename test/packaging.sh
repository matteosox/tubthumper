#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Testing packaging"

docker/run.sh --name test_packaging \
    test/inner_packaging.sh

echo "$(basename "$0") completed successfully!"
