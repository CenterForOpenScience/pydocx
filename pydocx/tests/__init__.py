from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import posixpath
import re
from contextlib import contextmanager
from xml.dom import minidom

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO
    BytesIO = StringIO

from pydocx.wordml import MainDocumentPart, WordprocessingDocument
from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.utils import (
    parse_xml_from_string,
)
from pydocx.tests.document_builder import DocxBuilder as DXB
from unittest import TestCase

STYLE = (
    '<style>'
    '.pydocx-caps {text-transform:uppercase}'
    '.pydocx-center {text-align:center}'
    '.pydocx-comment {color:blue}'
    '.pydocx-delete {color:red;text-decoration:line-through}'
    '.pydocx-hidden {visibility:hidden}'
    '.pydocx-insert {color:green}'
    '.pydocx-left {text-align:left}'
    '.pydocx-right {text-align:right}'
    '.pydocx-small-caps {font-variant:small-caps}'
    '.pydocx-strike {text-decoration:line-through}'
    '.pydocx-tab {display:inline-block;width:4em}'
    '.pydocx-underline {text-decoration:underline}'
    'body {margin:0px auto;width:51.00em}'
    '</style>'
)

BASE_HTML = '''
<html>
    <head>
    %s
    </head>
    <body>%%s</body>
</html>
''' % STYLE


def prettify(xml_string):
    """Return a pretty-printed XML string for the Element.
    """
    parsed = minidom.parseString(xml_string)
    return parsed.toprettyxml(indent='\t')


def html_is_equal(a, b):
    a = collapse_html(a)
    b = collapse_html(b)
    return a == b


def assert_html_equal(actual_html, expected_html, filename=None):
    if not html_is_equal(actual_html, expected_html):
        html = prettify(actual_html)
        if filename:
            with open('pydocx/tests/failures/%s.html' % filename, 'w') as f:
                f.write(html)
        raise AssertionError(html)


def collapse_html(html):
    """
    Remove insignificant whitespace from the html.

    >>> print(collapse_html('''\\
    ...     <h1>
    ...         Heading
    ...     </h1>
    ... '''))
    <h1>Heading</h1>
    >>> print(collapse_html('''\\
    ...     <p>
    ...         Paragraph with
    ...         multiple lines.
    ...     </p>
    ... '''))
    <p>Paragraph with multiple lines.</p>
    """
    def smart_space(match):
        # Put a space in between lines, unless exactly one side of the line
        # break butts up against a tag.
        before = match.group(1)
        after = match.group(2)
        space = ' '
        if before == '>' or after == '<':
            space = ''
        return before + space + after
    # Replace newlines and their surrounding whitespace with a single space (or
    # empty string)
    html = re.sub(
        r'(>?)\s*\n\s*(<?)',
        smart_space,
        html,
    )
    return html.strip()


class XMLDocx2Html(Docx2Html):
    """
    Create the object without passing in a path to the document, set them
    manually.
    """
    def __init__(self, *args, **kwargs):
        # Pass in nothing for the path
        self.document_xml = kwargs.pop('document_xml')
        self.relationships = kwargs.pop('relationships')
        self.numbering_dict = kwargs.pop('numbering_dict', None) or {}
        self.styles_dict = kwargs.pop('styles_dict', None) or {}
        super(XMLDocx2Html, self).__init__(path=None, *args, **kwargs)

    def _load(self):
        self.document = WordprocessingDocument(path=None)
        package = self.document.package
        document_part = package.create_part(
            uri='/word/document.xml',
        )

        if self.relationships:
            for relationship in self.relationships:
                target_mode = 'Internal'
                if relationship['external']:
                    target_mode = 'External'
                target_uri = relationship['target_path']
                if 'data' in relationship:
                    full_target_uri = posixpath.join(
                        package.uri,
                        'word',
                        target_uri,
                    )
                    package.streams[full_target_uri] = BytesIO(
                        relationship['data'],
                    )
                    package.create_part(uri=full_target_uri)
                document_part.create_relationship(
                    target_uri=target_uri,
                    target_mode=target_mode,
                    relationship_type=relationship['relationship_type'],
                    relationship_id=relationship['relationship_id'],
                )

        package.streams[document_part.uri] = BytesIO(self.document_xml)
        package.create_relationship(
            target_uri=document_part.uri,
            target_mode='Internal',
            relationship_type=MainDocumentPart.relationship_type,
        )

        self.numbering_root = None
        if self.numbering_dict is not None:
            self.numbering_root = parse_xml_from_string(
                DXB.numbering(self.numbering_dict),
            )

        # This is the standard page width for a word document (in points), Also
        # the page width that we are looking for in the test.
        self.page_width = 612

        self.parse_begin(self.document.main_document_part.root_element)

    def get_list_style(self, num_id, ilvl):
        try:
            return self.numbering_dict[num_id][ilvl]
        except KeyError:
            return 'decimal'


DEFAULT_NUMBERING_DICT = {
    '1': {
        '0': 'decimal',
        '1': 'decimal',
    },
    '2': {
        '0': 'lowerLetter',
        '1': 'lowerLetter',
    },
}


class _TranslationTestCase(TestCase):
    expected_output = None
    relationships = None
    styles_dict = None
    numbering_dict = DEFAULT_NUMBERING_DICT
    run_expected_output = True
    parser = XMLDocx2Html
    use_base_html = True
    convert_root_level_upper_roman = False

    def get_xml(self):
        raise NotImplementedError()

    @contextmanager
    def toggle_run_expected_output(self):
        self.run_expected_output = not self.run_expected_output
        yield
        self.run_expected_output = not self.run_expected_output

    def test_expected_output(self):
        if self.expected_output is None:
            raise NotImplementedError('expected_output is not defined')
        if not self.run_expected_output:
            return

        # Create the xml
        tree = self.get_xml()

        # Verify the final output.
        parser = self.parser

        html = parser(
            convert_root_level_upper_roman=self.convert_root_level_upper_roman,
            document_xml=tree,
            relationships=self.relationships,
            numbering_dict=self.numbering_dict,
            styles_dict=self.styles_dict,
        ).parsed

        if self.use_base_html:
            assert_html_equal(
                html,
                BASE_HTML % self.expected_output,
                filename=self.__class__.__name__,
            )
        else:
            assert_html_equal(
                html,
                self.expected_output,
                filename=self.__class__.__name__,
            )
