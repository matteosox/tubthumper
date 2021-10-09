#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Inner shell script for running unit tests

CMD=("coverage" "run")

usage()
{
    echo "usage: test/inner_unit_test.sh [--no-coverage -n]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -n | --no-coverage )
            CMD=("python")
            echo "Running unit tests without coverage tracking"
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            echo "Invalid inputs, see below"
            usage
            exit 2
            ;;
    esac
done

PYTHONHASHSEED=0 "${CMD[@]}" -m unittest discover --verbose --start-directory test
