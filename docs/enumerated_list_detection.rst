#########################
Enumerated List Detection
#########################

The default behavior
in PyDocX
is to convert
"faked" enumerated lists
into "real" enumerated lists.

A "faked" enumerated list
is a sequence of paragraphs
in which the numbering
has been explicitly
typed.
Additionally,
the spacing
across levels
is manually set
either using
tab characters,
or indentation.
For example: ::

    1. Apple
    2. Banana
       a. Chiquita
       b. Dole
    3. Carrot

Conversely,
a "real" enumerated list
is a sequence of paragraphs
in which the numbering,
and spacing,
is automatic:

#. Apple
#. Banana

   a. Chiquita
   #. Dole
#. Carrot

Supported enumeration sequences
###############################

* arabic numberals: 1, 2, 3, ...
* uppercase alphabet characters A, B, C, ..., Z, AA, AB, ... AZ, ...
* lowercase alphabet characters a, b, c, ..., z, aa, ab, ... az, ...
* uppercase Roman numberals: I, II, III, IV, ...
* lowercase Roman numberals: i, ii, iii, iv, ...

Supported enumeration patterns
##############################

* Digit followed by a dot plus space: "1. ", "A. ", "a. ", "I. ", "i. "
* Surrounded by parentheses: "(1)", "(A)", "(a)", "(I)", "(i)"
* Digit followed by a parenthesis: "1)", "A)", "a)", "I)", "i)"

How to disable enumerated list detection
########################################

Extend the exporter
to override
the ``numbering_span_builder_class``
class variable
as follows:

.. code-block:: python

    from pydocx.export.numbering_span import BaseNumberingSpanBuilder

    class CustomExporter(PyDocXHTMLExporter):
        numbering_span_builder_class = BaseNumberingSpanBuilder
