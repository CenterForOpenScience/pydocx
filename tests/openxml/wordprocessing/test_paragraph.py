# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Paragraph
from pydocx.util.xml import parse_xml_from_string


class ParagraphTestBase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Paragraph.load(root)


class GetTextTestCase(ParagraphTestBase):
    def test_no_runs(self):
        xml = '<p/>'
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), '')

    def test_no_text_nodes_several_runs(self):
        xml = '<p><r /><r /></p>'
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), '')

    def test_only_non_text_children_in_run(self):
        xml = '<p><r><br /></r></p>'
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), '')

    def test_single_run_single_text_node(self):
        xml = '<p><r><t>foo</t></r></p>'
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), 'foo')

    def test_single_run_many_text_nodes(self):
        xml = '''
            <p>
                <r>
                    <t>a</t>
                    <t>b</t>
                    <t>c</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), 'abc')

    def test_many_runs_many_text_nodes(self):
        xml = '''
            <p>
                <r>
                    <t>a</t>
                    <t>b</t>
                </r>
                <r>
                    <t>c</t>
                    <t>d</t>
                </r>
                <r>
                    <t>e</t>
                    <t>f</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), 'abcdef')

    def test_single_run_many_text_nodes_with_non_text_nodes(self):
        xml = '''
            <p>
                <r>
                    <t>a</t>
                    <br />
                    <t>b</t>
                    <tab />
                    <t>c</t>
                    <noBreakHyphen />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_text(), 'abc')


class StripTextFromLeftTestCase(ParagraphTestBase):
    def test_single_run_single_text_node(self):
        xml = '''
            <p>
                <r>
                    <t>Foo Bar</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.strip_text_from_left('Foo ')
        self.assertEqual(paragraph.get_text(), 'Bar')

    def test_only_removes_if_leading_text_matches(self):
        xml = '''
            <p>
                <r>
                    <t>NO Foo Bar</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.strip_text_from_left('Foo')
        self.assertEqual(paragraph.get_text(), 'NO Foo Bar')

    def test_many_runs_many_text_nodes(self):
        xml = '''
            <p>
                <r>
                    <t>a</t>
                    <t>b</t>
                </r>
                <r>
                    <t>c</t>
                    <t>d</t>
                </r>
                <r>
                    <t>e</t>
                    <t>f</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.strip_text_from_left('abcde')
        self.assertEqual(paragraph.get_text(), 'f')

    def test_leading_non_text_is_ignored(self):
        xml = '''
            <p>
                <r>
                    <br />
                    <t>Foo Bar</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.strip_text_from_left('Foo ')
        self.assertEqual(paragraph.get_text(), 'Bar')

    def test_all_text_is_removed(self):
        xml = '''
            <p>
                <r>
                    <t>a</t>
                    <t>b</t>
                </r>
                <r>
                    <t>c</t>
                    <t>d</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.strip_text_from_left('abcd')
        self.assertEqual(paragraph.get_text(), '')


class GetNumberOfInitialTabsTestCase(ParagraphTestBase):
    def test_empty_paragraph(self):
        xml = '<p />'
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_empty_run(self):
        xml = '''
            <p>
                <r />
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_single_run_single_text_node(self):
        xml = '''
            <p>
                <r>
                    <t>Foo</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_single_initial_tab(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 1)

    def test_many_runs_many_tabs(self):
        xml = '''
            <p>
                <r>
                    <tab />
                    <tab />
                </r>
                <r>
                    <tab />
                </r>
                <r />
                <r>
                    <tab />
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 5)

    def test_break_tag_stops_counting(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
                <r>
                    <tab />
                    <br />
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 2)

    def test_text_node_stops_counting(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
                <r>
                    <tab />
                    <t>Foo</t>
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 2)

    def test_hyperlink_stops_counting(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
                <hyperlink />
                <r>
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 1)


class RemoveInitialTabsTestCase(ParagraphTestBase):
    def test_empty_paragraph(self):
        xml = '<p />'
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_single_run_single_text_node(self):
        xml = '''
            <p>
                <r>
                    <t>Foo</t>
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_single_initial_tab(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_many_runs_many_tabs(self):
        xml = '''
            <p>
                <r>
                    <tab />
                    <tab />
                </r>
                <r>
                    <tab />
                </r>
                <r />
                <r>
                    <tab />
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_break_tag_stops_counting(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
                <r>
                    <tab />
                    <br />
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_tabs_up_to_first_text_node_are_removed(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
                <r>
                    <tab />
                    <t>Foo</t>
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)

    def test_tabs_up_to_first_hyperlink_are_removed(self):
        xml = '''
            <p>
                <r>
                    <tab />
                </r>
                <hyperlink />
                <r>
                    <tab />
                </r>
            </p>
        '''
        paragraph = self._load_from_xml(xml)
        paragraph.remove_initial_tabs()
        self.assertEqual(paragraph.get_number_of_initial_tabs(), 0)
