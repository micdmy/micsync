#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm -rf ${THIS_SCRIPT_DIR}/output/
rm -rf ${THIS_SCRIPT_DIR}/micsync/__pycache__/
rm -rf ${THIS_SCRIPT_DIR}/build/
rm -rf ${THIS_SCRIPT_DIR}/tests/__pycache__/
