from contextlib import contextmanager
from unittest import TestCase

from pydocx.test.utils import (
    Docx2HtmlNoStyle,
    html_is_equal,
    prettify,
    XMLDocx2Html,
    assert_html_equal,
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
    '''

    def assert_document_generates_html(self, document, expected_html):
        zip_buf = create_zip_archive(document.to_zip_dict())
        parser = Docx2HtmlNoStyle(zip_buf)
        actual = parser.parsed
        expected = BASE_HTML_NO_STYLE % expected_html
        if not html_is_equal(actual, expected):
            actual = prettify(actual)
            message = 'The expected HTML did not match the actual HTML:'
            raise AssertionError(message + '\n' + actual)


class TranslationTestCase(TestCase):
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

    def assert_expected_output(self):
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
