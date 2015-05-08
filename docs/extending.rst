################
Extending PyDocX
################

Customizing The Export
######################

``pydocx.export.PyDocXExporter``
includes abstracts methods
that each exporter implements
to satisfy its own needs.

The abstract methods are as follows:

.. code-block:: python

    class PyDocXExporter:

        @property
        def parsed(self):
            return self._parsed

        @property
        def escape(self, text):
            return text

        @abstractmethod
        def linebreak(self):
            return ''

        @abstractmethod
        def paragraph(self, text):
            return text

        @abstractmethod
        def heading(self, text, heading_level):
            return text

        @abstractmethod
        def insertion(self, text, author, date):
            return text

        @abstractmethod
        def hyperlink(self, text, href):
            return text

        @abstractmethod
        def image_handler(self, path):
            return path

        @abstractmethod
        def image(self, path, x, y):
            return self.image_handler(path)

        @abstractmethod
        def deletion(self, text, author, date):
            return text

        @abstractmethod
        def bold(self, text):
            return text

        @abstractmethod
        def italics(self, text):
            return text

        @abstractmethod
        def underline(self, text):
            return text

        @abstractmethod
        def superscript(self, text):
            return text

        @abstractmethod
        def subscript(self, text):
            return text

        @abstractmethod
        def tab(self):
            return True

        @abstractmethod
        def ordered_list(self, text):
            return text

        @abstractmethod
        def unordered_list(self, text):
            return text

        @abstractmethod
        def list_element(self, text):
            return text

        @abstractmethod
        def table(self, text):
            return text 
        @abstractmethod
        def table_row(self, text):
            return text

        @abstractmethod
        def table_cell(self, text):
            return text

        @abstractmethod
        def page_break(self):
            return True

        @abstractmethod
        def indent(self, text, left='', right='', firstLine=''):
            return text

Basic HTML exporting
is implemented in
``pydocx.export.PyDocXHTMLExporter``.
To override any specific default behavior,
simply extend the class
and implement the desired methods:

.. code-block:: python

    class MyPyDocXHTMLExporter(PyDocXExporter):

        #  Escape '&', '<', and '>' so we render the HTML correctly
        def escape(self, text):
            return xml.sax.saxutils.quoteattr(text)[1:-1]

        # return a line break
        def linebreak(self, pre=None):
            return '<br />'

        # add paragraph tags
        def paragraph(self, text, pre=None):
            return '<p class="foo">' + text + '</p>'


If you want to implement an exporter
for an unsupported markup language,
you can do that easily
by extending ``pydocx.export.PyDocXExporter``:

.. code-block:: python

    class CustomPyDocXExporter(PyDocXExporter):

        # because linebreaks in are denoted by '!!!!!!!!!!!!' with the FOO
        # markup langauge  :)
        def linebreak(self):
            return '!!!!!!!!!!!!'

Custom Pre-Processor
####################

When creating your own exporter
(as described above)
you can define
your own custom Pre Processor
by setting
the ``pre_processor``
field on the export subclass.

.. code-block:: python

    class MyPyDocXExporter(PyDocXExporter):
        pre_processor_class = MyPyDocXPreProcessor

    class MyPyDocXPreProcessor(PydocxPreProcessor):
        def perform_pre_processing(self, root, *args, **kwargs):
            super(MyPyDocXPreProcessor, self).perform_pre_processing(root, *args, **kwargs)
            self._set_foo(root)

        def _set_foo(self, root):
            pass

If you want ``_set_foo``
to be called
you must add it
to ``perform_pre_processing``
which is called from
``pydocx.export.PyDocXExporter``.

Everything done during pre-processing
is executed prior to ``parse``
being called for the first time.
