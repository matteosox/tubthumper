#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/strict_mode.sh

# Shell script that wraps `docker run` to keep
# volume mount, user switch, and --rm option

CMD=("bash")
OPTIONS=()

usage()
{
    echo "usage: run.sh [--env -e ENV] [-it] --name -n NAME [CMD ...]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -n | --name )
            NAME="$2"
            shift 2
            ;;
        -e | --env )
            OPTIONS+=("--env" "$2")
            shift 2
            ;;
        -it )
            OPTIONS+=("--interactive" "--tty")
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            OLD_IFS="$IFS"
            IFS=" " read -r -a CMD <<< "$@"
            IFS="$OLD_IFS"
            break
            ;;
    esac
done

if [[ -z "${NAME-}" ]]; then
    echo "Required input --name not provided, see below"
    usage
    exit 1
else
    OPTIONS+=("--name" "$NAME")
fi

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)

docker run \
    --rm \
    "${OPTIONS[@]}" \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/cicd/tubthumper \
    matteosox/tubthumper-cicd \
    "${CMD[@]}"
