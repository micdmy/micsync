#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm -rf ${THIS_SCRIPT_DIR}/build/ ${THIS_SCRIPT_DIR}/dist/ ${THIS_SCRIPT_DIR}/micsync_micdmy.egg-info/ ${THIS_SCRIPT_DIR}/micsync/__pycache__/ ${THIS_SCRIPT_DIR}/PKGBUILD

