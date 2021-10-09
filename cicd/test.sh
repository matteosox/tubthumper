#! /usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR"/../docker/strict_mode.sh

echo "Running tests"

UNIT_TESTS_CMD=("test/unit_tests.sh")

usage()
{
    echo "usage: cicd/test.sh [--all -a]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -a | --all )
            UNIT_TESTS_CMD+=("--tox")
            echo "Running full test suite"
            shift 1
            ;;
        -h | --help )
            usage
            exit 0
            ;;
        * )
            echo "Invalid inputs, see below"
            usage
            exit 2
            ;;
    esac
done

NC='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
LIGHT_CYAN='\033[0;36m'

NOT_STARTED="${RED}NOT STARTED${LIGHT_CYAN}"
RUNNING="${RED}RUNNING${LIGHT_CYAN}"
FAILED="${RED}FAILED${LIGHT_CYAN}"
SUCCESS="${GREEN}SUCCESS${LIGHT_CYAN}"

VERSION_STATUS="$NOT_STARTED"
REQUIREMENTS_STATUS="$NOT_STARTED"
BLACK_STATUS="$NOT_STARTED"
ISORT_STATUS="$NOT_STARTED"
PYLINT_STATUS="$NOT_STARTED"
SHELLCHECK_STATUS="$NOT_STARTED"
MYPY_STATUS="$NOT_STARTED"
UNIT_TESTS_STATUS="$NOT_STARTED"
PACKAGING_STATUS="$NOT_STARTED"
DOCS_STATUS="$NOT_STARTED"
EXIT_CODE=0

report_status() {
    if [[ "$EXIT_CODE" == 0 ]]; then
        TEST_STATUS="$SUCCESS"
    else
        TEST_STATUS=" $FAILED"
    fi

    echo -e "${LIGHT_CYAN}
Test Summary: $TEST_STATUS
=====================
  - Version: $VERSION_STATUS
  - Requirements: $REQUIREMENTS_STATUS
  - Black: $BLACK_STATUS
  - isort: $ISORT_STATUS
  - Pylint: $PYLINT_STATUS
  - ShellCheck: $SHELLCHECK_STATUS
  - Mypy: $MYPY_STATUS
  - Unit Tests: $UNIT_TESTS_STATUS
  - Packaging Tests: $PACKAGING_STATUS
  - Docs Tests: $DOCS_STATUS
${NC}"
}
trap report_status EXIT


echo -e "${LIGHT_CYAN}
Running version check
=====================
${NC}"
VERSION_STATUS="$RUNNING"
if test/version.sh; then
    VERSION_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    VERSION_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Version check completed w/ status: $VERSION_STATUS


Running requirements check
==========================
${NC}"
REQUIREMENTS_STATUS="$RUNNING"
if test/requirements.sh; then
    REQUIREMENTS_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    REQUIREMENTS_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Requirements check completed w/ status: $REQUIREMENTS_STATUS


Running Black
=============
${NC}"
BLACK_STATUS="$RUNNING"
if test/black.sh --diff --check; then
    BLACK_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    BLACK_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Black completed w/ status: $BLACK_STATUS


Running isort
=============
${NC}"
ISORT_STATUS="$RUNNING"
if test/isort.sh --check-only; then
    ISORT_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    ISORT_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
isort completed w/ status: $ISORT_STATUS


Running Pylint
==============
${NC}"
PYLINT_STATUS="$RUNNING"
if test/pylint.sh; then
    PYLINT_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    PYLINT_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Pylint completed w/ status: $PYLINT_STATUS


Running ShellCheck
==================
${NC}"
SHELLCHECK_STATUS="$RUNNING"
if test/shellcheck.sh; then
    SHELLCHECK_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    SHELLCHECK_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
ShellCheck completed w/ status: $SHELLCHECK_STATUS


Running Mypy
============
${NC}"
MYPY_STATUS="$RUNNING"
if test/mypy.sh; then
    MYPY_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    MYPY_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Mypy completed w/ status: $MYPY_STATUS


Running unit tests
==================
${NC}"
UNIT_TESTS_STATUS="$RUNNING"
if "${UNIT_TESTS_CMD[@]}"; then
    UNIT_TESTS_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    UNIT_TESTS_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Unit tests completed w/ status: $UNIT_TESTS_STATUS


Running packaging tests
=======================
${NC}"
PACKAGING_STATUS="$RUNNING"
if test/packaging.sh; then
    PACKAGING_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    PACKAGING_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Packaging tests completed w/ status: $PACKAGING_STATUS


Running documentation tests
===========================
${NC}"
DOCS_STATUS="$RUNNING"
if docs/build.sh; then
    DOCS_STATUS="$SUCCESS"
else
    EXIT_CODE=1
    DOCS_STATUS="$FAILED"
fi
echo -e "${LIGHT_CYAN}
Documentation tests completed w/ status: $DOCS_STATUS

${NC}"
exit $EXIT_CODE
