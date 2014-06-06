from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import os
import posixpath
import re
import tempfile
from contextlib import contextmanager
from xml.dom import minidom

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO
    BytesIO = StringIO

from pydocx.managers.styles import StylesManager
from pydocx.wordml import (
    MainDocumentPart,
    StyleDefinitionsPart,
    WordprocessingDocument,
)
from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.util.xml import parse_xml_from_string
from pydocx.util.zip import ZipFile
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


BASE_HTML_NO_STYLE = '''
<html>
    <head></head>
    <body>%s</body>
</html>
'''


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


class Docx2HtmlNoStyle(Docx2Html):
    def style(self):
        return ''


class DocumentGeneratorTestCase(TestCase):
    '''
    A test case class that can be inherited to compare xml fragments with their
    resulting HTML output.  This is achieved by generating a document container
    on the fly in a temporary location and then using the parser to convert
    that document.
    Each test case needs to call `assert_xml_body_matches_expected_html`
    '''

    def wrap_body_xml(self, body_xml):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <document><body>%s</body></document>
        ''' % body_xml
        return xml

    def wrap_style_xml(self, style_xml):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <styles>%s</styles>
        ''' % style_xml
        return xml

    @contextmanager
    def build_and_convert_document_to_html(self, body=None, style=None):
        fixture_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'fixtures',
        )
        docx_structure_fixture = os.path.join(fixture_path, 'docx_structure')
        word_directory = os.path.join(docx_structure_fixture, 'word')
        document_xml_path = os.path.join(word_directory, 'document.xml')
        style_xml_path = os.path.join(word_directory, 'styles.xml')
        files_to_cleanup = []
        try:
            if body is not None:
                with open(document_xml_path, 'w') as f:
                    f.write(self.wrap_body_xml(body))
                files_to_cleanup.append(document_xml_path)
            if style is not None:
                with open(style_xml_path, 'w') as f:
                    f.write(self.wrap_style_xml(style))
                files_to_cleanup.append(style_xml_path)
            zip_file = tempfile.NamedTemporaryFile()
            with ZipFile(zip_file.name, 'w') as zf:
                for root, dirs, files in os.walk(docx_structure_fixture):
                    for f in files:
                        full_path = os.path.join(root, f)
                        arcname = os.path.relpath(
                            full_path,
                            docx_structure_fixture,
                        )
                        zf.write(full_path, arcname)
            yield zip_file.name
        finally:
            for f in files_to_cleanup:
                os.unlink(f)

    def assert_xml_body_matches_expected_html(
        self,
        body,
        expected,
        style=None,
    ):
        '''
        Given an XML body, generate a document container, then convert that
        container to HTML and compare it with the given result.
        '''
        manager = self.build_and_convert_document_to_html(
            body=body,
            style=style,
        )
        with manager as docx_path:
            actual = Docx2HtmlNoStyle(docx_path).parsed
            expected = BASE_HTML_NO_STYLE % expected
            if not html_is_equal(actual, expected):
                actual = prettify(actual)
                message = 'The expected HTML did not match the actual HTML:'
                raise AssertionError(message + '\n' + actual)


class XMLDocx2Html(Docx2Html):
    """
    Create the object without passing in a path to the document, set them
    manually.
    """
    def __init__(self, *args, **kwargs):
        # Pass in nothing for the path
        self.document_xml = kwargs.pop('document_xml')
        self.relationships = kwargs.pop('relationships') or []
        self.numbering_dict = kwargs.pop('numbering_dict', None) or {}
        self.styles_xml = kwargs.pop('styles_xml', '')
        super(XMLDocx2Html, self).__init__(path=None, *args, **kwargs)

    def _load(self):
        self.document = WordprocessingDocument(path=None)
        package = self.document.package
        document_part = package.create_part(
            uri='/word/document.xml',
        )

        if self.styles_xml:
            self.relationships.append({
                'external': False,
                'target_path': 'styles.xml',
                'data': self.styles_xml,
                'relationship_id': 'styles',
                'relationship_type': StyleDefinitionsPart.relationship_type,
            })

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

        self.styles_manager = StylesManager(
            self.document.main_document_part.style_definitions_part,
        )
        self.styles = self.styles_manager.styles

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
    numbering_dict = DEFAULT_NUMBERING_DICT
    run_expected_output = True
    parser = XMLDocx2Html
    use_base_html = True
    convert_root_level_upper_roman = False
    styles_xml = None

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
            styles_xml=self.styles_xml,
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
