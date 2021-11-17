#!/bin/bash

set -e

PACKAGE="dist/$(basename `pwd`)_$(date +"%Y-%m-%d_%H-%M-%S").zip"
mkdir -p dist
zip -r ${PACKAGE} . -x '.*/*' 'env/*' '**__pycache__/*' '**/*.pyc' '.pytest_cache/*' '*.iml' '*.sqlite3' 'dist/*'

echo
echo "${PACKAGE} saved!"

