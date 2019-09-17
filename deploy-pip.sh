#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${THIS_SCRIPT_DIR}

#TEST SERVER:
#python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

#OFFICIAL SERVER:
python3 -m twine upload ${THIS_SCRIPT_DIR}/dist/*
