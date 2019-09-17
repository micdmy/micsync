#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${THIS_SCRIPT_DIR}

python3 ${THIS_SCRIPT_DIR}/setup.py sdist bdist_wheel

cp ${THIS_SCRIPT_DIR}/PKGBUILD-template ${THIS_SCRIPT_DIR}/PKGBUILD

package_name="$(python3 ${THIS_SCRIPT_DIR}/setup.py --fullname)"
full_package_path="${THIS_SCRIPT_DIR}/dist/${package_name}.tar.gz"
checksum=($(md5sum $full_package_path))
line_for_PKGBUILD="md5sums=('$checksum')"
echo $line_for_PKGBUILD >> ${THIS_SCRIPT_DIR}/PKGBUILD 
