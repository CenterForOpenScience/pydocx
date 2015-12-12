from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import os
from contextlib import contextmanager
from tempfile import mkstemp
from unittest import TestCase
from xml.parsers.expat import ExpatError

from pydocx.export.html import PyDocXHTMLExporter
from pydocx.openxml.packaging import MainDocumentPart
from pydocx.test.utils import (
    PyDocXHTMLExporterNoStyle,
    XMLDocx2Html,
    WordprocessingDocumentFactory,
    assert_html_equal,
    html_is_equal,
    prettify,
)
from pydocx.util.zip import create_zip_archive


STYLE = (
    '<style>'
    '.pydocx-caps {text-transform:uppercase}'
    '.pydocx-center {text-align:center}'
    '.pydocx-comment {color:blue}'
    '.pydocx-delete {color:red;text-decoration:line-through}'
    '.pydocx-hidden {visibility:hidden}'
    '.pydocx-insert {color:green}'
    '.pydocx-left {text-align:left}'
    '.pydocx-list-style-type-cardinalText {list-style-type:decimal}'
    '.pydocx-list-style-type-decimal {list-style-type:decimal}'
    '.pydocx-list-style-type-decimalEnclosedCircle {list-style-type:decimal}'
    '.pydocx-list-style-type-decimalEnclosedFullstop {list-style-type:decimal}'
    '.pydocx-list-style-type-decimalEnclosedParen {list-style-type:decimal}'
    '.pydocx-list-style-type-decimalZero {list-style-type:decimal-leading-zero}'  # noqa
    '.pydocx-list-style-type-lowerLetter {list-style-type:lower-alpha}'
    '.pydocx-list-style-type-lowerRoman {list-style-type:lower-roman}'
    '.pydocx-list-style-type-none {list-style-type:none}'
    '.pydocx-list-style-type-ordinalText {list-style-type:decimal}'
    '.pydocx-list-style-type-upperLetter {list-style-type:upper-alpha}'
    '.pydocx-list-style-type-upperRoman {list-style-type:upper-roman}'
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
    <meta charset="utf-8" />
    %s
    </head>
    <body>%%s</body>
</html>
''' % STYLE


BASE_HTML_NO_STYLE = '''
<html>
    <head><meta charset="utf-8" /></head>
    <body>%s</body>
</html>
'''

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


class DocumentGeneratorTestCase(TestCase):
    '''
    A test case class that can be inherited to compare xml fragments with their
    resulting HTML output.

    Each test case needs to call `assert_document_generates_html`

    `additional_parts` may be used to explicitly define additional parts to be
    included in the zip container. This is defined as a dictionary where the
    key is a path within the container, and the value is the data at that path.

    For example:

    additional_parts = {
        'word/media/foo.avi': 'data',
    }

    could be used as a way to include a non-standard video part with arbitrary
    data.
    '''

    exporter = PyDocXHTMLExporterNoStyle

    def assert_document_generates_html(
        self,
        document,
        expected_html,
        additional_parts=None,
        save_zip_on_failure=False,
    ):
        zip_archive = self.get_zip_archive_for_document(
            document,
            additional_parts=additional_parts,
        )
        exporter = self.exporter(zip_archive)
        actual = exporter.export()
        expected = self.format_expected_html(expected_html)
        if not html_is_equal(actual, expected):
            try:
                actual = prettify(actual)
            except ExpatError:
                pass
            message = [
                'The expected HTML did not match the actual HTML:',
                actual,
            ]
            if save_zip_on_failure:
                _, path_to_docx = mkstemp(suffix='.docx', prefix='pydocx-')
                with open(path_to_docx, 'w') as f:
                    zip_archive.seek(0)
                    f.write(zip_archive.read())
                message.append(
                    'The docx was saved to {path}'.format(path=path_to_docx),
                )
            raise AssertionError('\n'.join(message))

    def get_zip_archive_for_document(self, document, additional_parts=None):
        doc_zip_dict = document.to_zip_dict()
        if additional_parts:
            doc_zip_dict.update(additional_parts)
        return create_zip_archive(doc_zip_dict)

    def format_expected_html(self, html):
        return BASE_HTML_NO_STYLE % html

    def assert_main_document_xml_generates_html(self, main_document_xml, expected_html):
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, main_document_xml)
        self.assert_document_generates_html(document, expected_html)


class TranslationTestCase(TestCase):
    expected_output = None
    relationships = None
    numbering_dict = DEFAULT_NUMBERING_DICT
    run_expected_output = True
    parser = XMLDocx2Html
    use_base_html = True
    styles_xml = None

    def get_xml(self):
        raise NotImplementedError()

    @contextmanager
    def toggle_run_expected_output(self):
        self.run_expected_output = not self.run_expected_output
        yield
        self.run_expected_output = not self.run_expected_output

    def assert_expected_output(self):
        if self.expected_output is None:
            raise NotImplementedError('expected_output is not defined')
        if not self.run_expected_output:
            return

        # Create the xml
        tree = self.get_xml()

        # Verify the final output.
        export_class = self.parser

        exporter = export_class(
            document_xml=tree,
            relationships=self.relationships,
            numbering_dict=self.numbering_dict,
            styles_xml=self.styles_xml,
        )
        html = exporter.export()

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

    def test_expected_output(self):
        if self.expected_output is None:
            return
        self.assert_expected_output()


class DocXFixtureTestCaseFactory(TestCase):
    cases_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        '..',
        'tests',
        'fixtures',
    )
    exporter = PyDocXHTMLExporter

    @classmethod
    def create(cls, name):
        def run_test(self):
            docx_path = self.get_path_to_fixture('%s.docx' % name)
            expected_path = self.get_path_to_fixture('%s.html' % name)

            expected = ''
            with open(expected_path) as f:
                expected = f.read()

            expected = BASE_HTML % expected
            result = self.convert_docx_to_html(docx_path)

            self.assertHtmlEqual(result, expected)
        return run_test

    @classmethod
    def generate(cls):
        for case in cls.cases:
            test_method = cls.create(case)
            name = str('test_%s' % case)
            test_method.__name__ = name
            setattr(cls, name, test_method)

    def convert_docx_to_html(self, path_to_docx, *args, **kwargs):
        exporter = self.exporter(path_to_docx, *args, **kwargs)
        return exporter.export()

    def assertHtmlEqual(self, actual, expected):
        if not html_is_equal(actual, expected):
            actual = prettify(actual)
            message = 'The expected HTML did not match the actual HTML:'
            raise AssertionError(message + '\n' + actual)

    def get_path_to_fixture(self, fixture):
        return os.path.join(self.cases_path, fixture)
