#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${THIS_SCRIPT_DIR}
VIRT_ENV_DIR="${THIS_SCRIPT_DIR}/virt_env_for_test"

python -m venv ${VIRT_ENV_DIR}
cp -r ${THIS_SCRIPT_DIR}/tests ${VIRT_ENV_DIR}
source ${VIRT_ENV_DIR}/bin/activate 

print("hello")

