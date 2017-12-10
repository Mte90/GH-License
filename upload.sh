#!/bin/bash

echo "Upload in progress of the package to PyPi"

python setup.py sdist
twine upload dist/*
