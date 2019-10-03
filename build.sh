#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${THIS_SCRIPT_DIR}

OUTPUT_DIR="${THIS_SCRIPT_DIR}/output"
mkdir ${OUTPUT_DIR}

python3 ${THIS_SCRIPT_DIR}/setup.py build --build-base=${OUTPUT_DIR}/build egg_info --egg-base=${OUTPUT_DIR} sdist --dist-dir=${OUTPUT_DIR}/dist bdist_wheel --dist-dir=${OUTPUT_DIR}/dist


cp ${THIS_SCRIPT_DIR}/PKGBUILD-template ${OUTPUT_DIR}/PKGBUILD

package_name="$(python3 ${THIS_SCRIPT_DIR}/setup.py --fullname)"
package_version="$(python3 ${THIS_SCRIPT_DIR}/setup.py --version)"
full_package_path="${OUTPUT_DIR}/dist/${package_name}.tar.gz"
checksum=($(md5sum $full_package_path))
line_for_PKGBUILD="md5sums=('$checksum')"
echo $line_for_PKGBUILD >> ${OUTPUT_DIR}/PKGBUILD 
sed --in-place "s/VERSION_PLACEHOLDER/${package_version}/" ${OUTPUT_DIR}/PKGBUILD
