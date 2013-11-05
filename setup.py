#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages  # noqa
rel_file = lambda *args: os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *args)


def get_file(filename):
    with open(rel_file(filename)) as f:
        return f.read()


def get_description():
    return get_file('README.rst') + get_file('CHANGELOG')

setup(
    name="PyDocX",
    # Edit here and pydocx.__init__
    version="0.3.13",
    description="docx (OOXML) to html converter",
    author="Jason Ward, Sam Portnow",
    author_email="jason.louard.ward@gmail.com, samson91787@gmail.com",
    url="http://github.com/OpenScienceFramework/pydocx",
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    package_data={
        'pydocx': [
            'tests/templates/*.xml',
        ],
    },
    scripts=[],
    zip_safe=False,
    install_requires=[],
    cmdclass={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    long_description=get_description(),
    entry_points={
        'console_scripts': [
            'pydocx = pydocx.__init__:main',
        ],
    },
)
