#!/bin/bash
python3 setup.py sdist bdist_wheel
 python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

#python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-your-username

