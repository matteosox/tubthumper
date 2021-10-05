#! /usr/bin/env bash
set -euf -o pipefail

# Updates the requirements.txt file

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/../requirements

export CUSTOM_COMPILE_COMMAND="requirements/update.sh"

pip-compile --allow-unsafe --verbose docs_requirements.in > docs_requirements.txt
pip-compile --allow-unsafe --verbose test_requirements.in > test_requirements.txt
pip-compile --allow-unsafe --verbose requirements.in > requirements.txt
