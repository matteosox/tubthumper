#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Shell script for running unit tests

CMD=("test/inner_unit_tests.sh" "--no-coverage")

usage()
{
    echo "usage: unit_tests.sh [--tox -t] -- [Options for tox]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -t | --tox )
            CMD=("tox")
            echo "Using tox"
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        -- )
            OLD_IFS="$IFS"
            IFS=" " read -r -a OPTS <<< "$@"
            IFS="$OLD_IFS"
            echo "Using custom options ${OPTS[*]}"
            CMD=("${CMD[@]}" "${OPTS[@]}")
            break
            ;;
        * )
            echo "Invalid inputs, see below"
            usage
            exit 2
            ;;
    esac
done

if [[ "${CMD[0]}" == "tox" ]]; then
    cleanup() {
        rm -rf tubthumper.egg-info
        if [[ -e .coverage ]]; then
            mv .coverage reports/coverage
        fi
        rm -f .coverage.*
    }
    trap cleanup EXIT

    if [[ ! -d ".cache/tox" ]]; then
        echo "Initializing tox environment"
        docker/run.sh --name init_tox --env TOX_PARALLEL_NO_SPINNER=1 \
            tox --notest --parallel
    fi
fi

echo "Running unit tests"
docker/run.sh --name unit_tests \
    "${CMD[@]}"

echo "$(basename "$0") completed successfully!"
