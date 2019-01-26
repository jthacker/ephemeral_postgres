#!/bin/bash
set -e
TWINE_USERNAME=${TWINE_USERNAME:?}
TWINE_PASSWORD=${TWINE_PASSWORD:?}

python setup.py sdist
twine check dist/*
twine upload dist/*
