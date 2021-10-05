#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

if ! version/check.sh is_final; then
    echo "Not publishing since this is not a final release"
    exit 0
fi

echo "Publishing package to PyPI"

publish/package.sh --repository pypi

echo "All done!"
