======
pydocx
======
.. image:: https://travis-ci.org/OpenScienceFramework/pydocx.png?branch=master
   :align: left
   :target: https://travis-ci.org/OpenScienceFramework/pydocx

pydocx is a parser that breaks down the elements of a docxfile and converts them
into different markup languages. Right now, HTML is supported. Markdown and LaTex
will be available soon. You can extend any of the available parsers to customize it
to your needs. You can also create your own class that inherits DocxParser
to create your own methods for a markup language not yet supported.

Currently Supported
###################

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

Usage
#####

DocxParser includes abstracts methods that each parser overwrites to satsify its own needs. The abstract methods are as follows:

::

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

Docx2Html inherits DocxParser and implements basic HTML handling. Ex.

::

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


However, let's say you want to add a specific style to your HTML document. In order to do this, you want to make each paragraph a class of type `my_implementation`. Simply extend docx2Html and add what you need.

::

     class My_Implementation_of_Docx2Html(Docx2Html):

        def paragraph(self, text, pre = None):
            return <p class="my_implementation"> + text + '</p>'



OR, let's say FOO is your new favorite markup language. Simply customize your own new parser, overwritting the abstract methods of DocxParser

::

    class Docx2Foo(DocxParser):

        # because linebreaks in are denoted by '!!!!!!!!!!!!' with the FOO markup langauge  :)
        def linebreak(self):
            return '!!!!!!!!!!!!'


Styles
######

The base parser `Docx2Html` relies on certain css class being set for certain behaviour to occur. Currently these include:

* class `pydocx-insert` -> Turns the text green.
* class `pydocx-delete` -> Turns the text red and draws a line through the text.
* class `pydocx-center` -> Aligns the text to the center.
* class `pydocx-right` -> Aligns the text to the right.
* class `pydocx-left` -> Aligns the text to the left.
* class `pydocx-comment` -> Turns the text blue.
* class `pydocx-underline` -> Underlines the text.

Optional Arguments
##################

You can pass in `convert_root_level_upper_roman=True` to the parser and it will convert all root level upper roman lists to headings instead.
