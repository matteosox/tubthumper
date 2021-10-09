#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/../docker/strict_mode.sh"

# Inner shell script for updating requirements

export CUSTOM_COMPILE_COMMAND="requirements/update.sh"

pip-compile --allow-unsafe --verbose requirements/docs_requirements.in > requirements/docs_requirements.txt
pip-compile --allow-unsafe --verbose requirements/test_requirements.in > requirements/test_requirements.txt
pip-compile --allow-unsafe --verbose requirements/requirements.in > requirements/requirements.txt
