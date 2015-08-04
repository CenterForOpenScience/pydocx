#####
Usage
#####

Converting files using the command line interface
#################################################

Using the ``pydocx`` command,
you can specify the output format
with the input and output files:

.. code-block:: shell-session

    $ pydocx --html input.docx output.html

Converting files using the library directly
###########################################

If you don't want to mess around
having to create exporters,
you can use the
``PyDocX.to_html``
helper method:

.. code-block:: python

    from pydocx import PyDocX

    # Pass in a path
    html = PyDocX.to_html('file.docx')

    # Pass in a file object
    html = PyDocX.to_html(open('file.docx', 'rb'))

    # Pass in a file-like object
    from cStringIO import StringIO
    buf = StringIO()
    with open('file.docx') as f:
       buf.write(f.read())

    html = PyDocX.to_html(buf)


Of course,
you can do the same using the exporter
class:

.. code-block:: python

    from pydocx.export import PyDocXHTMLExporter

    # Pass in a path
    exporter = PyDocXHTMLExporter('file.docx')
    html = exporter.export()

    # Pass in a file object
    exporter = PyDocXHTMLExporter(open('file.docx', 'rb'))
    html = exporter.export()

    # Pass in a file-like object
    from cStringIO import StringIO
    buf = StringIO()
    with open('file.docx') as f:
       buf.write(f.read())

    exporter = PyDocXHTMLExporter(buf)
    html = exporter.export()

Currently Supported HTML elements
#################################

* tables

  * nested tables
  * rowspans
  * colspans
  * lists in tables

* lists

  * list styles
  * nested lists
  * list of tables
  * list of pragraphs

* justification
* images
* styles

  * bold
  * italics
  * underline
  * hyperlinks

* headings

HTML Styles
###########

The export class
``pydocx.export.PyDocXHTMLExporter``
relies on certain
CSS classes being defined
for certain behavior to occur.

Currently these include:

* class ``pydocx-insert`` -> Turns the text green.
* class ``pydocx-delete`` -> Turns the text red and draws a line through the text.
* class ``pydocx-center`` -> Aligns the text to the center.
* class ``pydocx-right`` -> Aligns the text to the right.
* class ``pydocx-left`` -> Aligns the text to the left.
* class ``pydocx-comment`` -> Turns the text blue.
* class ``pydocx-underline`` -> Underlines the text.
* class ``pydocx-caps`` -> Makes all text uppercase.
* class ``pydocx-small-caps`` -> Makes all text uppercase, however truly lowercase letters will be small than their uppercase counterparts.
* class ``pydocx-strike`` -> Strike a line through.
* class ``pydocx-hidden`` -> Hide the text.
* class ``pydocx-tab`` -> Represents a tab within the document.

Additionally,
several list styles are defined
based off the attribute values
listed at:
http://officeopenxml.com/WPnumbering-numFmt.php

* class ``pydocx-list-style-type-cardinalText`` -> (1, 2, 3, 4, etc.)
* class ``pydocx-list-style-type-decimal`` -> (1, 2, 3, 4, etc.)
* class ``pydocx-list-style-type-decimalEnclosedCircle`` -> (1, 2, 3, 4, etc.)
* class ``pydocx-list-style-type-decimalEnclosedFullstop`` -> (1, 2, 3, 4, etc.)
* class ``pydocx-list-style-type-decimalEnclosedParen`` -> (1, 2, 3, 4, etc.)
* class ``pydocx-list-style-type-decimalZero`` -> (01, 02, 03, etc.)
* class ``pydocx-list-style-type-lowerLetter`` -> (a, b, c, etc.)
* class ``pydocx-list-style-type-lowerRoman`` -> (i, ii, iii, etc.)
* class ``pydocx-list-style-type-none`` -> List style is removed
* class ``pydocx-list-style-type-ordinalText`` -> (1, 2, 3, 4, etc.)
* class ``pydocx-list-style-type-upperLetter`` -> (A, B, C, etc.)
* class ``pydocx-list-style-type-upperRoman`` -> (I, II, III, etc.)

Exceptions
##########

There is only one custom exception (``MalformedDocxException``).
It is raised if either the ``xml`` or ``zipfile`` libraries raise an exception.
