#!/bin/bash

python3 setup.py sdist bdist_wheel

cp ./PKGBUILD-template ./PKGBUILD

full_package_name="./dist/$(python3 setup.py --fullname).tar.gz"
checksum=($(md5sum ./$full_package_name))
line_for_PKGBUILD="md5sums=('$checksum')"
echo $line_for_PKGBUILD >> PKGBUILD 
