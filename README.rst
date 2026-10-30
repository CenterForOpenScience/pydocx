PyDocX
======

.. image:: https://github.com/CenterForOpenScience/pydocx/actions/workflows/ci.yml/badge.svg?branch=master
   :alt: CI
   :target: https://github.com/CenterForOpenScience/pydocx/actions/workflows/ci.yml

PyDocX is an extensible Python library for reading Microsoft Word DOCX
(Office Open XML) documents and exporting their content to markup.

It includes an HTML exporter and a command-line interface. Developers can
customize the HTML output or implement exporters for other markup formats
using the underlying document model and export framework.

Features
--------

* Built-in DOCX-to-HTML conversion.
* Support for headings, paragraphs, text formatting, hyperlinks, and images.
* Support for nested lists and tables, including merged cells.
* Customizable export behavior through exporter subclasses.
* Input from file paths, binary file objects, or file-like objects.

HTML is the built-in output format. Other formats require a custom exporter.
PyDocX does not aim to reproduce Word's page layout exactly.

Installation
------------

.. code-block:: console

   pip install pydocx

Quick start
-----------

Convert a document from the command line:

.. code-block:: console

   pydocx --html input.docx output.html

Or use the Python API:

.. code-block:: python

   from pydocx import PyDocX

   html = PyDocX.to_html("input.docx")

You can also pass an open binary file:

.. code-block:: python

   from pydocx import PyDocX

   with open("input.docx", "rb") as document:
       html = PyDocX.to_html(document)

Custom exporters
----------------

Use ``PyDocXHTMLExporter`` directly when you need control over HTML
conversion:

.. code-block:: python

   from pydocx.export import PyDocXHTMLExporter

   exporter = PyDocXHTMLExporter("input.docx")
   html = exporter.export()

Subclass ``PyDocXHTMLExporter`` to customize HTML output, or
``pydocx.export.base.PyDocXExporter`` to implement another markup format.

See the `extension guide
<https://pydocx.readthedocs.org/en/latest/extending.html>`_
for details.

Documentation and support
-------------------------

* `Documentation <https://pydocx.readthedocs.org/en/latest/>`_
* `Usage guide <https://pydocx.readthedocs.org/en/latest/usage.html>`_
* `Release notes <https://pydocx.readthedocs.org/en/latest/release_notes.html>`_
* `Source code <https://github.com/CenterForOpenScience/pydocx>`_
* `Report an issue <https://github.com/CenterForOpenScience/pydocx/issues>`_

Contributing
------------

Bug reports, documentation improvements, and code contributions are welcome.
When reporting a conversion problem, include your Python and PyDocX versions,
the expected output, and a minimal DOCX example with sensitive information
removed.

License
-------

PyDocX is licensed under the Apache License, Version 2.0.
See the LICENSE file for details.
