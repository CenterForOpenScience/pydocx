################
Extending PyDocX
################

Customizing the HTML Exporter
#############################

Basic HTML exporting
is implemented in
``pydocx.export.html.PyDocXHTMLExporter``.
To override default behavior,
simply extend the class
and implement the desired methods.
Here are a few examples
to show you what is possible:

.. code-block:: python

    class MyPyDocXHTMLExporter(PyDocXExporter):

        def __init__(self, path):
            # Handle dstrike the same as italic
            self.export_run_property_dstrike = self.export_run_property_italic

            super(MyPyDocXHTMLExporter, self).__init__(path=path)

        # Perform specific pre-processing
        def export(self):
            self.delete_only_FOO_text_nodes()
            return super(MyPyDocXHTMLExporter, self).export()

        def delete_only_FOO_text_nodes(self):
            # Delete all text nodes that match 'FOO' exactly
            document = self.main_document_part.document
            for body_child in document.body.children:
                if isinstance(body_child, wordprocessing.Paragraph):
                    paragraph = body_child
                    for paragraph_child in paragraph.children:
                        if isinstance(paragraph_child, wordprocessing.Run):
                            run = paragraph_child
                            for run_child in run.children[:]:
                                if isinstance(run_child, wordprocessing.Text):
                                    text = run_child
                                    if text.text == 'FOO'
                                        run.children.remove(text)

        # Don't display head
        def head(self):
            return
            # The exporter expects all methods to return a generator
            yield  # this syntax causes an empty generator to be returned

        # Ignore page break
        def get_break_tag(self, br):
            if br.is_page_break():
                pass
            else:
                return super(MyPyDocXHTMLExporter, self).get_break_tag(br)

        # Do not show deleted runs
        def export_deleted_run(self, deleted_run):
            return
            yield

        # Custom table tag
        def get_table_tag(self, table):
            attrs = {
                'class': 'awesome-table',
            }
            return HtmlTag('table', **attrs)

        # By default, the HTML exporter wraps inserted runs in a span with
        # class="pydocx-insert". This example overrides that method to skip
        # that behavior by jumping to the base implementation.
        def export_inserted_run(self, inserted_run):
            return super(PyDocXExporter, self).export_inserted_run(inserted_run)

        # Hide hidden runs
        def export_run(self, run):
            properties = run.effective_properties
            if properties.vanish:
                return
            elif properties.hidden:
                return
            results = super(MyPyDocXHTMLExporter, self).export_run(run)
            for result in results:
                yield result

Implementing a new exporter
###########################

If you want to implement an exporter
for an unsupported markup language,
you can do that
by extending
``pydocx.export.base.PyDocXExporter``
as needed.
For example,
this shows how you might
create a custom exporter
for the FML,
or Foo Markup Language:

.. code-block:: python

    class PyDocXFOOExporter(PyDocXExporter):

        # The "FOO" markup language denotes breaks using "\"
        def export_break(self):
            yield '\\'

        def export_document(self, document):
            yield 'START OF DOC'
            results = super(PyDocXFOOExporter, self).export_document(self, document)
            for result in results:
                yield result
            yield 'END OF DOC'

        # Text must be wrapped in ()
        def export_text(self, text):
            yield '({0})'.format(text.text)

        # Tables are denoted by [ ]
        def export_table(self, table):
            yield '['
            results = super(PyDocXFOOExporter, self).export_table(self, table)
            for result in results:
                yield result
            yield ']'

        # Table rows are denoted by { }
        def export_table_row(self, table_row):
            yield '{'
            results = super(PyDocXFOOExporter, self).export_table_row(self, table_row)
            for result in results:
                yield result
            yield '}'

        # Table cells are denoted by < >
        def export_table_row(self, table_cell):
            yield '<'
            results = super(PyDocXFOOExporter, self).export_table_cell(self, table_cell)
            for result in results:
                yield result
            yield '>'

The base exporter implementation
expects all methods
to return a generator.
For this reason,
it is not possible
to have an empty
method (``pass``)
or have a method
that just returns ``None``.
The one caveat
is the special syntax
that causes a method
to return an empty
generator:

.. code-block:: python

    def empty_generator():
        return
        yield

This implementation
is consistent with the
"only generators"
rule,
and is actually
computationally faster
than returning
an empty list.
