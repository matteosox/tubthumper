#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

EXIT_CODE=0
SHELL_SCRIPTS=$(git ls-files | grep ".*\.sh$")
declare -A STATUSES

report_status() {
    echo "Shellcheck Summary"
    for script in $SHELL_SCRIPTS; do
        status=${STATUSES[$script]:-"NOT STARTED"}
        echo "  - $script: $status"
    done
}
trap report_status EXIT

for script in $SHELL_SCRIPTS; do
    STATUSES[$script]=RUNNING
    if shellcheck "$script"; then
        STATUSES[$script]=SUCCESS
    else
        EXIT_CODE=1
        STATUSES[$script]=FAILED
    fi
done

exit $EXIT_CODE
