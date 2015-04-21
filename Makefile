.PHONY: help clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rmdir {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 pydocx tests

test:
	nosetests --verbose --with-doctest --with-coverage --cover-package pydocx

test-all:
	tox

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

release: clean
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist

wheel: clean
	python setup.py bdist_wheel
	ls -l dist
