#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Shell script for testing the version

MAIN_BRANCH=main

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" == "$MAIN_BRANCH" ]]; then
    echo "Current branch is $CURRENT_BRANCH, so skipping version check"
    exit 0
fi

echo "Checking version to make sure it is updated appropriately"

BASE_REF=$(git merge-base remotes/origin/"$MAIN_BRANCH" HEAD)
echo "Best common ancestor of current branch with $MAIN_BRANCH is $BASE_REF"
MAIN_VERSION=$(git show "$BASE_REF":tubthumper/VERSION)
echo "Version from best common ancestor is $MAIN_VERSION"

if ! version/check.sh current_supersedes --version "$MAIN_VERSION"; then
    echo "
Current version does not supersede version from $MAIN_BRANCH
To fix this, run version/increment.sh"
    exit 1
fi

echo "$(basename "$0") completed successfully!"
