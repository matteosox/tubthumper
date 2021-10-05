#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

CMD=("test/inner_unit_tests.sh" "--no-coverage")

usage()
{
    echo "usage: unit_tests.sh [--tox -t] -- [Options for tox]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -t | --tox )
            CMD=("tox")
            echo "Running Python unit tests with tox"
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        -- )
            shift 1
            IFS=" " read -r -a OPTS <<< "$@"
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

echo "Running unit tests"

LOCAL_GROUP_ID=$(id -g)

if [[ ! -d ".tox" && "${CMD[0]}" == "tox" ]]; then
    echo "Initializing tox environment"
    docker run \
        --rm \
        --name init_tox \
        --user "1024:$LOCAL_GROUP_ID" \
        --volume "$REPO_DIR":/home/cicd/tubthumper \
        matteosox/tubthumper-cicd \
        tox --notest --parallel
fi

docker run \
    --rm \
    --name unit_tests \
    --user "1024:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    "${CMD[@]}"
