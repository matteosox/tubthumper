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

echo "Checking version to make sure it isn't identical to any previous versions"

CURR_VERSION=$(cat tubthumper/VERSION)
echo "Current version is $CURR_VERSION"

echo "Previous versions"
PREV_REFS=$(git log remotes/origin/"$MAIN_BRANCH" --pretty=format:"%h")
for PREV_REF in $PREV_REFS; do
    PREV_VERSION=$(git show "$PREV_REF":tubthumper/VERSION)
    echo "$PREV_VERSION"
    if [[ "$CURR_VERSION" == "$PREV_VERSION" ]]; then
        echo "Current version is identical to version from $MAIN_BRANCH"
        echo "To fix this, increment it."
        exit 1
    fi
done

echo "$0 completed successfully!"
