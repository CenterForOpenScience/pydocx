from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import posixpath
import re
from contextlib import contextmanager
from xml.dom import minidom
from unittest import TestCase

try:
    from cString import StringIO
    BytesIO = StringIO
except ImportError:
    from io import BytesIO

from pydocx.managers.styles import StylesManager
from pydocx.packaging import PackageRelationship
from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.tests.document_builder import DocxBuilder as DXB
from pydocx.util.xml import parse_xml_from_string
from pydocx.util.zip import create_zip_archive
from pydocx.wordml import (
    MainDocumentPart,
    NumberingDefinitionsPart,
    StyleDefinitionsPart,
    WordprocessingDocument,
)

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

    base_relationships = '''
        <Relationships xmlns="{PackageRelationshipNamespace}">
          <Relationship Id="rId1" Type="{MainDocumentPartNamespace}"
            Target="word/document.xml"/>
        </Relationships>
    '''.format(
        PackageRelationshipNamespace=PackageRelationship.namespace,
        MainDocumentPartNamespace=MainDocumentPart.relationship_type,
    )

    content_types = '''
        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
          <Override PartName="/_rels/.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
          <Override PartName="/word/_rels/document.xml.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
          <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
          <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
        </Types>
    '''  # noqa

    def wrap_xml(self, xml):
        return '<?xml version="1.0" encoding="UTF-8"?>%s' % xml

    def wrap_body_xml(self, xml):
        xml = '<document><body>%s</body></document>' % xml
        return self.wrap_xml(xml)

    def wrap_style_xml(self, xml):
        xml = '<styles>%s</styles>' % xml
        return self.wrap_xml(xml)

    def wrap_numbering_xml(self, xml):
        xml = '<numbering>%s</numbering>' % xml,
        return self.wrap_xml(xml)

    def wrap_relationship_xml(self, xml):
        xml = '''
            <Relationships xmlns="{namespace}">
            {xml}
            </Relationships>
        '''.format(
            namespace=PackageRelationship.namespace,
            xml=xml,
        )
        return self.wrap_xml(xml)

    @contextmanager
    def build_and_convert_document_to_html(
        self,
        body=None,
        style=None,
        numbering=None,
        word_relationships=None,
    ):
        default_word_relationships = '''
          <Relationship Id="rId1" Type="{styles_rel_type}"
            Target="styles.xml"/>
          <Relationship Id="rId2" Type="{numbering_rel_type}"
            Target="numbering.xml"/>
        '''.format(
            styles_rel_type=StyleDefinitionsPart.relationship_type,
            numbering_rel_type=NumberingDefinitionsPart.relationship_type,
        )

        if word_relationships is None:
            word_relationships = default_word_relationships

        if word_relationships:
            word_relationships = self.wrap_relationship_xml(word_relationships)

        if body:
            body = self.wrap_body_xml(body)

        if style:
            style = self.wrap_style_xml(style)

        if numbering:
            numbering = self.wrap_numbering_xml(numbering)

        document = {
            '_rels/.rels': self.base_relationships,
            'word/_rels/document.xml.rels': word_relationships,
            'word/document.xml': body,
            'word/styles.xml': style,
            'word/numbering.xml': numbering,
            '[Content_Types].xml': self.content_types,
        }

        yield create_zip_archive(document)

    def assert_xml_body_matches_expected_html(self, expected, **kwargs):
        '''
        Given an XML body, generate a document container, then convert that
        container to HTML and compare it with the given result.
        '''
        manager = self.build_and_convert_document_to_html(**kwargs)
        with manager as docx_path:
            parser = Docx2HtmlNoStyle(docx_path)
            actual = parser.parsed
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
