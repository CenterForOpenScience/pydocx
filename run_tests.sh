#! /bin/sh

nosetests --verbose --with-doctest --with-coverage --cover-package pydocx $@
find -name '*.py' | xargs flake8
