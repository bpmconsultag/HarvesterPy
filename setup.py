
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Setup script for HarvesterPy
#
# Copyright: (c) 2024, bpmconsultag
# MIT License

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="harvesterpy",
    version="0.1.0",
    author="bpmconsultag",
    description="A Python library to interface with SUSE Harvester HCI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bpmconsultag/HarvesterPy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
)
