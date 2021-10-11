#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Inner shell script for running unit tests with tox

if [[ ! -d "$HOME/.cache/tox" ]]; then
    echo "Initializing tox environment"
    TOX_PARALLEL_NO_SPINNER=1 tox --notest --parallel
fi

cleanup() {
    mv .coverage docs/source/_static/coverage &> /dev/null && true
    rm -f .coverage.*
}
trap cleanup EXIT

tox "$@"
