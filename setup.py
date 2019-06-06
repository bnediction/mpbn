#!/usr/bin/env python
# -*- coding: utf-8

import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

NAME = "mpbn"

META = {}
META_FILE = os.path.join(NAME, "__init__.py")
with open(META_FILE) as f:
    __data = f.read()
for key in ["version"]:
    match = re.search(r"^__{0}__ = ['\"]([^'\"]*)['\"]".format(key), __data, re.M)
    if not match:
        raise RuntimeError("Unable to find __{meta}__ string.".format(meta=key))
    META[key] = match.group(1)

setup(name = NAME,
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
    description = "Simple implementation of most permissive semantics of Boolean networks",
#    long_description=open('README.rst').read(),
    install_requires = [
        "colomoto_jupyter",
    ],
    entry_points = {
        "console_scripts": [
            "mpbn=mpbn.cli:main",
        ],
    },
    #include_package_data = True,
    packages = [NAME],
    **META
)

