#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ${THIS_SCRIPT_DIR}

OUTPUT_DIR="${THIS_SCRIPT_DIR}/output"
mkdir ${OUTPUT_DIR}

ver_from_file="$( cat micsync/version.py | sed "s/__version__ = \"//" | sed "s/\"//" )"
ver_from_git="$( git describe --abbrev=0 )"
if [ $ver_from_file != $ver_from_git ]; then
	read -p "Git tag not updated, continue? [Y/n]" -n 1 -r
	echo
	if [[ ! $REPLY =~ ^[Yy]$ ]]
	then
		    exit 1
	fi
fi

python3 ${THIS_SCRIPT_DIR}/setup.py build --build-base=${OUTPUT_DIR}/build egg_info --egg-base=${OUTPUT_DIR} sdist --dist-dir=${OUTPUT_DIR}/dist bdist_wheel --dist-dir=${OUTPUT_DIR}/dist


cp ${THIS_SCRIPT_DIR}/PKGBUILD-template ${OUTPUT_DIR}/PKGBUILD

#Add checksum to PKGBUILD:
package_name="$(python3 ${THIS_SCRIPT_DIR}/setup.py --fullname)"
package_version="$(python3 ${THIS_SCRIPT_DIR}/setup.py --version)"
full_package_path="${OUTPUT_DIR}/dist/${package_name}.tar.gz"
checksum=($(md5sum $full_package_path))
line_for_PKGBUILD="md5sums=('$checksum')"
echo $line_for_PKGBUILD >> ${OUTPUT_DIR}/PKGBUILD 
sed --in-place "s/VERSION_PLACEHOLDER/${package_version}/" ${OUTPUT_DIR}/PKGBUILD

#Create PKGBUILD for offline install, for developer convenience:
offline_build_dir="${OUTPUT_DIR}/offline-PKGBUILD"
mkdir ${offline_build_dir}
cp ${OUTPUT_DIR}/PKGBUILD ${offline_build_dir}/
package_file="${package_name}.tar.gz"
ln ${OUTPUT_DIR}/dist/${package_file} ${offline_build_dir}/${package_file}
sed --in-place "s/^source.*/source=('${package_file}')/" ${offline_build_dir}/PKGBUILD

