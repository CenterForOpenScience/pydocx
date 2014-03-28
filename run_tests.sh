#! /bin/sh

nosetests --verbose --with-doctest --with-coverage --cover-package pydocx $@ && find pydocx -name '*.py' | xargs flake8
