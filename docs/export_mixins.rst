#############
Export Mixins
#############

Export mixins
provide standardized
optional overrides
for specific use cases.
They exist in
``pydocx.export.mixins``.
Each mixin is defined as a class
in its own module.

Detect faked superscript and subscript
######################################

Useful if you want
runs of text
that are styled smaller
(relative to surrounding text)
and positioned
either above
or below
the surrounding text
to be treated as super/subscript.

Example usage:

.. code-block:: python

    from pydocx.export.mixins import FakedSuperscriptAndSubscriptExportMixin


    class CustomExporter(
        FakedSuperscriptAndSubscriptExportMixin,
        PyDocXHTMLExporter,
    ):
        pass
