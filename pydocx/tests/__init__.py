#from unittest import TestCase
import re

from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.DocxParser import (
    remove_namespaces,
    # We are only importing this from DocxParse since we have added methods to
    # it there.
    ElementTree,
)
from unittest import TestCase


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
    def _build_data(self, document_xml=None, *args, **kwargs):
        # Intentionally not calling super
        if document_xml is not None:
            self.root = ElementTree.fromstring(
                remove_namespaces(document_xml),
            )
        self.relationship_text = '<xml></xml>'

    def head(self):
        return ''


class _TranslationTestCase(TestCase):
    expected_output = None

    def get_xml(self):
        raise NotImplementedError()

    def test_expected_output(self):
        if self.expected_output is None:
            raise AssertionError('expected_output is not defined')

        # Create the xml
        tree = self.get_xml()

        # Verify the final output.
        html = XMLDocx2Html(document_xml=tree).parsed

        assert_html_equal(html, self.expected_output)
