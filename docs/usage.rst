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

Choose the conversing class,
and then pass in
either the full path
to an existing MS Word document
on the filesystem
or
pass in
a file-like object.
The parsed content can then be accessed
using the `parsed` attribute.

Examples:

.. code-block:: python

   from pydocx.parsers import Docx2Html

   # Pass in a path to an existing file
   parser = Docx2Html(path='file.docx')
   print parser.parsed

   # Pass in a file pointer
   parser = Docx2Html(open('file.docx'))
   print parser.parsed

   # Pass in a file-like object
   from cStringIO import StringIO
   buf = StringIO()
   with open('file.docx') as f:
      buf.write(f.read())
   parser = Docx2Html(buf)
   print parser.parsed

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

The base parser ``Docx2Html`` relies on certain css class being set for certain behaviour to occur.
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

Exceptions
##########

There is only one custom exception (``MalformedDocxException``).
It is raised if either the ``xml`` or ``zipfile`` libraries raise an exception.

Deviations from the `ECMA-376 <http://www.ecma-international.org/publications/standards/Ecma-376.htm>`_ Specification
#####################################################################################################################

Missing val attribute in underline tag
======================================

* In the event that the ``val`` attribute is missing from a ``u`` (``ST_Underline`` type),
  we treat the underline as off, or none.
  See also http://msdn.microsoft.com/en-us/library/ff532016%28v=office.12%29.aspx

   If the val attribute is not specified, Word defaults to the value defined in the style hierarchy and then to no underline.
