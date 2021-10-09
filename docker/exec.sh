#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/strict_mode.sh

# Shell script for running a command inside docker

OPTS=()
NAME=tubthumper-cicd

usage()
{
    echo "usage: exec.sh [--env -e ENV] [CMD ...]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -e | --env )
            OPTS+=("--env" "$2")
            shift 2
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            IFS=" " read -r -a CMD <<< "$@"
            break
            ;;
    esac
done

STATE=$(docker ps --all --filter "name=$NAME" --format "{{.State}}")

if [[ -z "$STATE" ]]; then
    echo "No Docker container found, so setting it up for you"
    cicd/setup.sh
fi

if [[ "$STATE" == "paused" ]]; then
    echo "Unpausing Docker container"
    docker unpause "$NAME"
elif [[ "$STATE" == "exited" ]]; then
    echo "Starting Docker container"
    docker start "$NAME"
fi

if [[ -z "${CMD[0]-}" ]]; then
    OPTS+=("--interactive" "--tty")
    CMD=("bash")
fi

OPTS+=("$NAME")
EXEC_CMD=("${OPTS[@]}" "${CMD[@]}")

restart_timer() {
    mkdir -p .cache
    touch "$TIMER_FILE"
}
trap restart_timer EXIT

docker exec "${EXEC_CMD[@]}"
