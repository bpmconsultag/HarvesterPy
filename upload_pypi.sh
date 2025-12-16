#!/bin/bash
set -e -x

python -m build
python -m twine upload dist/*

# For TestPyPI use the following commands:
twine upload --repository testpypi dist/*
# Install from test PyPI but prefer requirements from the official PyPI
# pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ harvesterpy==0.1.4

# For PyPI use the following commands:
# twine upload dist/*
# pip install harvesterpy==0.1.4