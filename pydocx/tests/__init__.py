#from unittest import TestCase
import re
from contextlib import contextmanager

from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.DocxParser import (
    remove_namespaces,
    # We are only importing this from DocxParse since we have added methods to
    # it there.
    ElementTree,
)
from unittest import TestCase

STYLE = (
    '<style>'
    '.pydocx-insert {color:green;}'
    '.pydocx-delete {color:red;text-decoration:line-through;}'
    '.pydocx-center {text-align:center;}'
    '.pydocx-right {text-align:right;}'
    '.pydocx-left {text-align:left;}'
    '.pydocx-comment {color:blue;}'
    '.pydocx-underline {text-decoration: underline;}'
    'body {width:612px;margin:0px auto;}'
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


def assert_html_equal(actual_html, expected_html):
    assert collapse_html(
        actual_html,
    ) == collapse_html(
        expected_html
    ), actual_html


def collapse_html(html):
    """
    Remove insignificant whitespace from the html.

    >>> print collapse_html('''\\
    ...     <h1>
    ...         Heading
    ...     </h1>
    ... ''')
    <h1>Heading</h1>
    >>> print collapse_html('''\\
    ...     <p>
    ...         Paragraph with
    ...         multiple lines.
    ...     </p>
    ... ''')
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
    def _build_data(
            self,
            document_xml=None,
            rels_dict=None,
            numbering_dict=None,
            styles_dict=None,
            *args, **kwargs):
        self._test_rels_dict = rels_dict
        if numbering_dict is None:
            numbering_dict = {}
        self.numbering_dict = numbering_dict
        # Intentionally not calling super
        if document_xml is not None:
            self.root = ElementTree.fromstring(
                remove_namespaces(document_xml),
            )
        self.zip_path = ''

        # This is the standard page width for a word document, Also the page
        # width that we are looking for in the test.
        self.page_width = 612

        self.styles_dict = styles_dict

    def _parse_rels_root(self, *args, **kwargs):
        if self._test_rels_dict is None:
            return {}
        return self._test_rels_dict

    def get_list_style(self, num_id, ilvl):
        try:
            return self.numbering_dict[num_id][ilvl]
        except KeyError:
            return 'decimal'

    def _parse_styles(self):
        if self.styles_dict is None:
            return {}
        return self.styles_dict


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
    relationship_dict = None
    styles_dict = None
    numbering_dict = DEFAULT_NUMBERING_DICT
    run_expected_output = True
    parser = XMLDocx2Html
    use_base_html = True

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
        html = self.parser(
            document_xml=tree,
            rels_dict=self.relationship_dict,
            numbering_dict=self.numbering_dict,
            styles_dict=self.styles_dict,
        ).parsed

        if self.use_base_html:
            assert_html_equal(html, BASE_HTML % self.expected_output)
        else:
            assert_html_equal(html, self.expected_output)
