###########
Development
###########

Installing requirements
#######################

Using pip
=========

.. code-block:: shell-session

   $ pip install -r requirements/docs.txt -r requirements/testing.txt

Using `terrarium <https://github.com/PolicyStat/terrarium>`_
============================================================

Terrarium will package up and compress a virtualenv for you based on pip
requirements and then let you ship that environment around.

.. code-block:: shell-session

   $ terrarium install requirements/*.txt

Building the documentation locally
##################################

#. Install the documentation requirements:

   .. code-block:: shell-session

      $ pip install -r requirements/docs.txt

#. Change directory to ``docs`` and run ``make html``:

   .. code-block:: shell-session

      $ cd docs
      $ make html

#. Load HTML documentation in a web browser of your choice:

   .. code-block:: shell-session

      $ firefox docs/_build/html/index.html

Running tests
#############

#. Install the development requirements:

   .. code-block:: shell-session

      $ pip install -r requirements/testing.txt

#. Run ``make test lint``
   in the project root.
   This will
   run ``nosetests``
   with coverage
   and also
   display any
   ``flake8`` errors.

   .. code-block:: shell-session

      $ make test lint

To run all tests against all supported versions of python,
use ``tox``.

Running tests with tox
======================

``tox`` allows us to use
one command to
run tests against
all versions of python
that we support.

Setting up tox
--------------

#. Decide how you want to manage multiple python versions.

   #. System level using a package manager such as ``apt-get``.
      This approach will likely require adding additional
      ``apt-get`` sources
      in order to install
      alternative versions of python.
   #. Use `pyenv <https://github.com/yyuu/pyenv-installer#installation>`_
      to manage and install multiple python versions.
      After installation,
      see the
      `pyenv command reference <https://github.com/yyuu/pyenv/blob/master/COMMANDS.md>`_.

#. Install ``tox``.

   .. code-block:: shell-session

       $ pip install tox

#. `Configure tox <http://tox.readthedocs.org/en/latest>`_.

Running tox
-----------

Now that you have ``tox`` setup, you just need to run the command ``tox`` from the project root directory.

.. code-block:: shell-session

   $ tox

Getting involved
################

The PyDocX project welcomes help in any of the following ways:

* Making pull requests on github for code,
  tests and documentation.
* Participating on open issues and pull requests,
  reviewing changes

Coding Standards
################

* All python source files **must** be
  `PEP8 <http://legacy.python.org/dev/peps/pep-0008>`_
  compliant.
* All python source files **must** include the following import declaration
  at the top of the file:

  .. code-block:: python

      from __future__ import (
          absolute_import,
          print_function,
          unicode_literals,
      )

Unicode Data
============

* All stream data is assumed to be a UTF-8 bytestream unless specified
  otherwise.
  What this means is that when you are writing test cases for a particular function,
  any input data you define which would have otherwise have come from a file source
  must be encoded as UTF-8.

Release process
###############

PyDocX adheres to
`Semantic versioning
v2.0.0
<http://semver.org/spec/v2.0.0.html>`_.

#. Update
   `CHANGELOG <https://github.com/CenterForOpenScience/pydocx/blob/master/CHANGELOG.rst>`_.
#. Bump the version number in
   `__init__.py <https://github.com/CenterForOpenScience/pydocx/blob/master/pydocx/__init__.py>`_
   on master.
#. Tag the version.
#. Push to PyPI

  .. code-block:: shell-session

    make release
