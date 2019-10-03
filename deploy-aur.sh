#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pkgbuild_file="${THIS_SCRIPT_DIR}/output/PKGBUILD"
pkgver="$(cat ${pkgbuild_file} | grep pkgver= | sed s/pkgver=//)"
archive_output_dir="${THIS_SCRIPT_DIR}/archive-pkgbuild/${pkgver}/"
mkdir ${archive_output_dir}
cp ${pkgbuild_file} ${archive_output_dir}

