#!/usr/bin/env python
# -*- coding: utf-8

import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

NAME = "mpbn"
VERSION = "9999"

setup(name = NAME,
    version = VERSION,
    author = "Loïc Paulevé",
    author_email = "loic.pauleve@ens-cachan.org",
    url = "https://github.com/pauleve/mpbn",
    license = "CeCILL",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords='',
    description = "Simple implementation of Most Permissive semantics of Boolean networks",
    long_description=open('README.md').read(),
    install_requires = [
        "boolean.py",
        "colomoto_jupyter",
    ],
    entry_points = {
        "console_scripts": [
            "mpbn=mpbn.cli:main",
        ],
    },
    #include_package_data = True,
    packages = [NAME]
)

