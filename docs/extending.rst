################
Extending PyDocX
################

Customizing The Parser
######################

``DocxParser`` includes abstracts methods that each parser overwrites to satisfy its own needs.
The abstract methods are as follows:

.. code-block:: python

    class DocxParser:

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

``Docx2Html`` inherits ``DocxParser`` and implements basic HTML handling.

.. code-block:: python

    class Docx2Html(DocxParser):

        #  Escape '&', '<', and '>' so we render the HTML correctly
        def escape(self, text):
            return xml.sax.saxutils.quoteattr(text)[1:-1]

        # return a line break
        def linebreak(self, pre=None):
            return '<br />'

        # add paragraph tags
        def paragraph(self, text, pre=None):
            return '<p>' + text + '</p>'


However,
let's say you want to add a specific style to your HTML document.
In order to do this, you want to make each paragraph a class of type ``my_implementation``.
Simply extend ``Docx2Html`` and add what you need.

.. code-block:: python

     class My_Implementation_of_Docx2Html(Docx2Html):

        def paragraph(self, text, pre = None):
            return <p class="my_implementation"> + text + '</p>'

OR,
let's say FOO is your new favorite markup language.
Simply customize your own new parser,
overwritting the abstract methods of ``DocxParser``.

.. code-block:: python

    class Docx2Foo(DocxParser):

        # because linebreaks in are denoted by '!!!!!!!!!!!!' with the FOO markup langauge  :)
        def linebreak(self):
            return '!!!!!!!!!!!!'

Custom Pre-Processor
####################

When creating your own Parser (as described above) you can now add in your own custom Pre Processor.
To do so you will need to set the ``pre_processor`` field on the custom parser.

.. code-block:: python

    class Docx2Foo(DocxParser):
        pre_processor_class = FooPreProcessor

The ``FooPreProcessor`` will need a few things to get you going:

.. code-block:: python

    class FooPreProcessor(PydocxPreProcessor):
        def perform_pre_processing(self, root, *args, **kwargs):
            super(FooPreProcessor, self).perform_pre_processing(root, *args, **kwargs)
            self._set_foo(root)

        def _set_foo(self, root):
            pass

If you want ``_set_foo`` to be called you must add it to ``perform_pre_processing`` which is called in the base parser for pydocx.

Everything done during pre-processing is executed prior to ``parse`` being called for the first time.

Optional Arguments
##################

You can pass in ``convert_root_level_upper_roman=True`` to the parser and it will convert all root level upper roman lists to headings instead.
