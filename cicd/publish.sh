#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

echo "Publishing package"

PUBLIC_RELEASE=$(docker/exec.sh publish/public_release.py)

if [[ "$PUBLIC_RELEASE" == "True" ]]; then
    echo "This is a public release"
    REPOSITORY="pypi"
    export TWINE_PASSWORD="$PYPI_TOKEN"
    TAG_ARG=""
else
    echo "This is a test release"
    REPOSITORY="testpypi"
    export TWINE_PASSWORD="$TESTPYPI_TOKEN"
    TAG_ARG="--draft"
fi

docker/exec.sh --env GITHUB_TOKEN \
    publish/tag.py "$TAG_ARG"

export TWINE_USERNAME="__token__"

docker/exec.sh --env TWINE_USERNAME --env TWINE_PASSWORD \
    publish/package.sh "$REPOSITORY"

echo "$0 completed successfully!"
