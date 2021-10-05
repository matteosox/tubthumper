#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

echo "Checking version to make sure it is updated appropriately"

MAIN_BRANCH=main
BASE_REF=$(git merge-base "$MAIN_BRANCH" HEAD)
echo "Best common ancestor of current branch with $MAIN_BRANCH is $BASE_REF"
MAIN_VERSION=$(git show "$BASE_REF":tubthumper/VERSION)
echo "Version from best common ancestor is $MAIN_VERSION"

if ! version/check.sh current_supersedes --version "$MAIN_VERSION"; then
    echo "
Current version does not supersede version from $MAIN_BRANCH
To fix this, run version/increment.sh"
    exit 1
fi
