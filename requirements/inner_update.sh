#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Inner shell script for updating requirements

export CUSTOM_COMPILE_COMMAND="requirements/update.sh"

pip-compile --allow-unsafe --resolver=backtracking --upgrade --verbose --output-file requirements/docs_requirements.txt requirements/docs_requirements.in
pip-compile --allow-unsafe --resolver=backtracking --upgrade --verbose --output-file requirements/test_requirements.txt requirements/test_requirements.in
pip-compile --allow-unsafe --resolver=backtracking --upgrade --verbose --output-file requirements/requirements.txt requirements/requirements.in
