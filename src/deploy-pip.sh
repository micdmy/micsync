#!/bin/bash

#TEST SERVER:
#python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

#OFFICIAL SERVER:
python3 -m twine upload dist/*
