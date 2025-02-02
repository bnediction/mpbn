#!/usr/bin/env python
# -*- coding: utf-8

from setuptools import setup, find_packages

NAME = "mpbn"
VERSION = "9999"

setup(name=NAME,
    version=VERSION,
    author="Loïc Paulevé",
    author_email="loic.pauleve@labri.fr",
    url="https://github.com/bnediction/mpbn",
    license="CeCILL",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords='',
    description="Simple implementation of Most Permissive Boolean networks",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "boolean.py",
        "clingo",
        "colomoto_jupyter>=0.8.0",
        "numpy",
        "biodivine_aeon>=1.0.1",
        "scipy",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "mpbn=mpbn.cli:main",
            "mpbn-sim=mpbn.cli.sim:main",
        ],
    },
    packages = find_packages(),
    package_data={'mpbn': ['asplib/*.asp']}
)
