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
            echo "Using tox"
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        -- )
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

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)

if [[ "${CMD[0]}" == "tox" ]]; then
    cleanup() {
        rm -rf tubthumper.egg-info
    }
    trap cleanup EXIT

    if [[ ! -d ".cache/tox" ]]; then
        echo "Initializing tox environment"
        docker run \
            --rm \
            --name init_tox \
            --env TOX_PARALLEL_NO_SPINNER=1 \
            --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
            --volume "$REPO_DIR":/home/cicd/tubthumper \
            matteosox/tubthumper-cicd \
            tox --notest --parallel
    fi
fi

echo "Running unit tests"

docker run \
    --rm \
    --name unit_tests \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    "${CMD[@]}"
