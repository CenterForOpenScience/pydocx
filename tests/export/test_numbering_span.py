# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import sys
from unittest import TestCase

from pydocx.export.numbering_span import NumberingSpanBuilder
from pydocx.openxml.wordprocessing import (
    Break,
    Paragraph,
    ParagraphProperties,
    NumberingProperties,
    Run,
    TabChar,
    Text,
    Numbering
)
from pydocx.util.xml import parse_xml_from_string


class NumberingSpanTestBase(TestCase):
    def setUp(self):
        self.builder = NumberingSpanBuilder()

    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Numbering.load(root)


class CleanParagraphTestCase(NumberingSpanTestBase):
    def test_empty_paragraph(self):
        paragraph = Paragraph()
        expected = Paragraph()

        self.builder.clean_paragraph(paragraph, 'Foo')
        self.assertEqual(repr(paragraph), repr(expected))


class RemoveInitialTextFromParagraphTestCase(NumberingSpanTestBase):
    def test_empty_paragraph(self):
        paragraph = Paragraph()
        expected = Paragraph()

        self.builder.remove_initial_text_from_paragraph(paragraph, 'Foo ')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_single_run_single_text_node(self):
        paragraph = Paragraph(children=[
            Run(children=[Text(text='Foo Bar')]),
        ])
        expected = Paragraph(children=[
            Run(children=[Text(text='Bar')]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'Foo ')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_only_removes_if_leading_text_matches(self):
        paragraph = Paragraph(children=[
            Run(children=[Text(text='NO Foo Bar')]),
        ])
        expected = Paragraph(children=[
            Run(children=[Text(text='NO Foo Bar')]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'Foo ')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_many_runs_many_text_nodes(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='a'),
                Text(text='b'),
            ]),
            Run(children=[
                Text(text='c'),
                Text(text='d'),
            ]),
            Run(children=[
                Text(text='e'),
                Text(text='f'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                Text(text=''),
            ]),
            Run(children=[
                Text(text=''),
                Text(text=''),
            ]),
            Run(children=[
                Text(text=''),
                Text(text='f'),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'abcde')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_leading_non_text_is_ignored(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Break(),
                Text(text='Foo Bar'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Break(),
                Text(text='Bar'),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'Foo ')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_all_text_is_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='a'),
                Text(text='b'),
            ]),
            Run(children=[
                Text(text='c'),
                Text(text='d'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                Text(text=''),
            ]),
            Run(children=[
                Text(text=''),
                Text(text=''),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'abcd')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_longer_text_after_split_matching_text_is_preserved(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='abcde'),
                Text(text='f'),
                # The key here is that the following text is longer that the
                # initial text, and the text above matches the initial text,
                # but is split.
                Text(text='ghijklm'),
                Text(text='nop'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                Text(text=''),
                Text(text='ghijklm'),
                Text(text='nop'),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'abcdef')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_initial_text_is_split_across_multiple_text_nodes(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='ab'),
                Text(text='cdef'),
                Text(text='chij'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                Text(text='def'),
                Text(text='chij'),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(paragraph, 'abc')
        self.assertEqual(repr(paragraph), repr(expected))

    def test_tabs_embedded_within_initial_text_can_be_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='a'),
                TabChar(),
                Text(text='b'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                Text(text=''),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(
            paragraph,
            initial_text='aFOOb',
            tab_char='FOO',
        )
        self.assertEqual(repr(paragraph), repr(expected))

    def test_tab_char_is_not_removed_when_tab_char_is_not_set(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='a'),
                TabChar(),
                Text(text='b'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                TabChar(),
                Text(text=''),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(
            paragraph,
            initial_text='ab',
        )
        self.assertEqual(repr(paragraph), repr(expected))

    def test_tab_char_is_not_removed_when_tab_char_does_not_match_text(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='a'),
                TabChar(),
                Text(text='b'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                TabChar(),
                Text(text='b'),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(
            paragraph,
            initial_text='aFOOb',
            tab_char='BAR',
        )
        self.assertEqual(repr(paragraph), repr(expected))

    def test_multiple_tab_chars_are_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[
                Text(text='a'),
                TabChar(),
                TabChar(),
                TabChar(),
                Text(text='b'),
            ]),
        ])
        expected = Paragraph(children=[
            Run(children=[
                Text(text=''),
                Text(text=''),
            ]),
        ])

        self.builder.remove_initial_text_from_paragraph(
            paragraph,
            initial_text='aFOOFOOFOOb',
            tab_char='FOO',
        )
        self.assertEqual(repr(paragraph), repr(expected))


class RemoveInitialTabCharsFromParagraphTestCase(NumberingSpanTestBase):
    def test_empty_paragraph_nothing_changes(self):
        paragraph = Paragraph()
        expected = Paragraph()

        self.builder.remove_initial_tab_chars_from_paragraph(paragraph)
        self.assertEqual(repr(paragraph), repr(expected))

    def test_single_run_single_text_node_no_tabs_nothing_changes(self):
        paragraph = Paragraph(children=[
            Run(children=[Text(text='Foo')]),
        ])
        expected = Paragraph(children=[
            Run(children=[Text(text='Foo')]),
        ])

        self.builder.remove_initial_tab_chars_from_paragraph(paragraph)
        self.assertEqual(repr(paragraph), repr(expected))

    def test_single_initial_tab_is_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[TabChar()]),
        ])
        expected = Paragraph(children=[
            Run(),
        ])

        self.builder.remove_initial_tab_chars_from_paragraph(paragraph)
        self.assertEqual(repr(paragraph), repr(expected))

    def test_many_runs_many_tabs_are_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[
                TabChar(),
                TabChar(),
            ]),
            Run(children=[
                TabChar(),
            ]),
            Run(),
            Run(children=[
                TabChar(),
                TabChar(),
            ]),
        ])
        expected = Paragraph(children=[
            Run(),
            Run(),
            Run(),
            Run(),
        ])

        self.builder.remove_initial_tab_chars_from_paragraph(paragraph)
        self.assertEqual(repr(paragraph), repr(expected))

    def test_only_tabs_before_break_are_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[
                TabChar(),
            ]),
            Run(children=[
                TabChar(),
                Break(),
                TabChar(),
            ]),
        ])
        expected = Paragraph(children=[
            Run(),
            Run(children=[
                Break(),
                TabChar(),
            ]),
        ])

        self.builder.remove_initial_tab_chars_from_paragraph(paragraph)
        self.assertEqual(repr(paragraph), repr(expected))

    def test_only_tabs_before_first_text_are_removed(self):
        paragraph = Paragraph(children=[
            Run(children=[
                TabChar(),
            ]),
            Run(children=[
                TabChar(),
                Text(),
                TabChar(),
            ]),
        ])
        expected = Paragraph(children=[
            Run(),
            Run(children=[
                Text(),
                TabChar(),
            ]),
        ])

        self.builder.remove_initial_tab_chars_from_paragraph(paragraph)
        self.assertEqual(repr(paragraph), repr(expected))


class DetectParentChildMapTestCase(NumberingSpanTestBase):
    def assertDictEqual(self, d1, d2, msg=None):
        if sys.version_info >= (2, 7):
            super(DetectParentChildMapTestCase, self).assertDictEqual(d1, d2, msg=msg)
        else:
            if d1 != d2:
                raise AssertionError("Dicts do not match: %s" % msg)

    def create_container(self):
        xml = '''
            <numbering>
                <abstractNum abstractNumId="1">
                    <lvl ilvl="0"></lvl>
                    <lvl ilvl="1"></lvl>
                    <lvl ilvl="2"></lvl>
                </abstractNum>
                <num numId="1">
                    <abstractNumId val="1" />
                </num>
                <abstractNum abstractNumId="2">
                    <lvl ilvl="0"></lvl>
                    <lvl ilvl="1"></lvl>
                    <lvl ilvl="2"></lvl>
                </abstractNum>
                <num numId="2">
                    <abstractNumId val="2" />
                </num>
                <abstractNum abstractNumId="3">
                    <lvl ilvl="0"></lvl>
                    <lvl ilvl="1"></lvl>
                    <lvl ilvl="2"></lvl>
                </abstractNum>
                <num numId="3">
                    <abstractNumId val="3" />
                </num>
                <abstractNum abstractNumId="4">
                    <lvl ilvl="0"></lvl>
                    <lvl ilvl="1"></lvl>
                    <lvl ilvl="2"></lvl>
                </abstractNum>
                <num numId="4">
                    <abstractNumId val="4" />
                </num>
                <abstractNum abstractNumId="5">
                    <lvl ilvl="0"></lvl>
                    <lvl ilvl="1"></lvl>
                    <lvl ilvl="2"></lvl>
                </abstractNum>
                <num numId="5">
                    <abstractNumId val="5" />
                </num>
            </numbering>
        '''

        numbering = self._load_from_xml(xml)

        container = type(
            str('Container'),
            (object,),
            {
                'numbering_definitions_part': type(str('Numbering'), (Numbering,),
                                                   {'numbering': numbering})
            }
        )

        return container

    def create_numbering_paragraph(self, num_id, level_id='0', container=True):
        paragraph_params = {
            'properties': ParagraphProperties(
                numbering_properties=NumberingProperties(
                    num_id=num_id,
                    level_id=level_id
                )
            )
        }

        if container:
            paragraph_params['container'] = self.create_container()

        return Paragraph(**paragraph_params)

    def test_no_components_on_init(self):
        builder = NumberingSpanBuilder()
        self.assertEqual(builder.child_parent_num_map, {})
        self.assertEqual(builder.parent_child_num_map, {})
        self.assertFalse(builder.detect_parent_child_map_for_items())

    def test_invalid_input_components(self):
        components = [
            Paragraph(),
            Paragraph(children=[
                Run(children=[
                    TabChar(),
                ])
            ]),
            Paragraph(
                properties=ParagraphProperties()
            ),
            Paragraph(
                properties=ParagraphProperties(
                    numbering_properties=NumberingProperties()
                )
            ),
            self.create_numbering_paragraph('1', '0', container=False),
        ]

        builder = NumberingSpanBuilder(components)
        self.assertEqual(builder.parent_child_num_map, {})
        self.assertEqual(builder.child_parent_num_map, {})
        self.assertFalse(builder.detect_parent_child_map_for_items())

    def test_valid_input_components_but_no_sublists_found(self):
        components = [
            Paragraph(),
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('3', '0'),
        ]

        list_start_stop_index = {
            '1': {'start': 1, 'stop': 2},
            '2': {'start': 3, 'stop': 4},
            '3': {'start': 5, 'stop': 6},
        }

        builder = NumberingSpanBuilder(components)
        self.assertEqual(builder.parent_child_num_map, {})
        self.assertEqual(builder.child_parent_num_map, {})
        self.assertEqual(builder.list_start_stop_index, list_start_stop_index)
        self.assertTrue(builder.detect_parent_child_map_for_items())

    def test_sublist_found(self):
        components = [
            Paragraph(),
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('1', '0'),
        ]

        builder = NumberingSpanBuilder(components)
        parent_items = {
            ('1', '0'):
                [
                    {'num_id': '2', 'level': '0'},
                ]
        }
        child_item = {
            '2': {'num_id': '1', 'level': '0'}
        }

        list_start_stop_index = {
            '1': {'start': 1, 'stop': 4},
            '2': {'start': 2, 'stop': 3},
        }

        self.assertDictEqual(builder.parent_child_num_map, parent_items)
        self.assertDictEqual(builder.child_parent_num_map, child_item)
        self.assertEqual(builder.list_start_stop_index, list_start_stop_index)
        self.assertTrue(builder.detect_parent_child_map_for_items())

    def test_nested_sublist_found(self):
        components = [
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('1', '0'),
        ]

        builder = NumberingSpanBuilder(components)

        parent_items = {
            ('1', '0'):
                [
                    {'num_id': '2', 'level': '0'},
                    {'num_id': '3', 'level': '0'},
                ],
            ('2', '0'):
                [
                    {'num_id': '3', 'level': '0'},
                ]
        }
        child_item = {
            '2': {'num_id': '1', 'level': '0'},
            '3': {'num_id': '2', 'level': '0'},
        }

        list_start_stop_index = {
            '1': {'start': 0, 'stop': 5},
            '2': {'start': 1, 'stop': 4},
            '3': {'start': 2, 'stop': 3},
        }

        self.assertDictEqual(builder.parent_child_num_map, parent_items)
        self.assertDictEqual(builder.child_parent_num_map, child_item)
        self.assertDictEqual(builder.list_start_stop_index, list_start_stop_index)
        self.assertTrue(builder.detect_parent_child_map_for_items())

    def test_nested_sublist_not_wrapped_in_parent_item(self):
        components = [
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('1', '0'),
        ]

        builder = NumberingSpanBuilder(components)

        parent_items = {
            ('1', '0'):
                [
                    {'num_id': '2', 'level': '0'},
                    {'num_id': '3', 'level': '0'},
                ]
        }
        child_item = {
            '2': {'num_id': '1', 'level': '0'},
            '3': {'num_id': '1', 'level': '0'},
        }

        list_start_stop_index = {
            '1': {'start': 0, 'stop': 4},
            '2': {'start': 1, 'stop': 1},
            '3': {'start': 2, 'stop': 3},
        }

        self.assertDictEqual(builder.parent_child_num_map, parent_items)
        self.assertDictEqual(builder.child_parent_num_map, child_item)
        self.assertDictEqual(builder.list_start_stop_index, list_start_stop_index)
        self.assertTrue(builder.detect_parent_child_map_for_items())

    def test_nested_sublist_parent_with_different_level(self):
        components = [
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('1', '1'),
            self.create_numbering_paragraph('3', '0'),
            Paragraph(),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('1', '1'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('2', '1'),
            self.create_numbering_paragraph('4', '0'),
            self.create_numbering_paragraph('4', '0'),
            self.create_numbering_paragraph('1', '0'),
            Paragraph(),
        ]

        builder = NumberingSpanBuilder(components)

        parent_items = {
            ('1', '0'):
                [
                    {'num_id': '3', 'level': '0'},
                    {'num_id': '2', 'level': '0'},
                    {'num_id': '2', 'level': '1'},
                    {'num_id': '4', 'level': '0'},
                ],
            ('1', '1'):
                [
                    {'num_id': '3', 'level': '0'},
                ]
        }
        child_item = {
            '2': {'num_id': '1', 'level': '0'},
            '3': {'num_id': '1', 'level': '1'},
            '4': {'num_id': '1', 'level': '0'},
        }

        list_start_stop_index = {
            '1': {'start': 0, 'stop': 10},
            '3': {'start': 2, 'stop': 4},
            '2': {'start': 6, 'stop': 6},
            '4': {'start': 8, 'stop': 9},
        }

        self.assertDictEqual(builder.parent_child_num_map, parent_items)
        self.assertDictEqual(builder.child_parent_num_map, child_item)
        self.assertDictEqual(builder.list_start_stop_index, list_start_stop_index)
        self.assertTrue(builder.detect_parent_child_map_for_items())

    def test_nested_sublist_multiple_levels(self):
        components = [
            self.create_numbering_paragraph('1', '0'),
            self.create_numbering_paragraph('1', '1'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('4', '0'),
            self.create_numbering_paragraph('3', '0'),
            self.create_numbering_paragraph('2', '0'),
            self.create_numbering_paragraph('1', '1'),
            self.create_numbering_paragraph('1', '0'),
        ]

        builder = NumberingSpanBuilder(components)

        parent_items = {
            ('1', '0'):
                [
                    {'num_id': '2', 'level': '0'},
                    {'num_id': '3', 'level': '0'},
                    {'num_id': '4', 'level': '0'},
                ],
            ('1', '1'):
                [
                    {'num_id': '2', 'level': '0'},
                    {'num_id': '3', 'level': '0'},
                    {'num_id': '4', 'level': '0'},
                ],
            ('2', '0'):
                [
                    {'num_id': '3', 'level': '0'},
                    {'num_id': '4', 'level': '0'},
                ],
            ('3', '0'):
                [
                    {'num_id': '4', 'level': '0'},
                ]
        }
        child_item = {
            '2': {'num_id': '1', 'level': '1'},
            '3': {'num_id': '2', 'level': '0'},
            '4': {'num_id': '3', 'level': '0'},
        }

        self.assertDictEqual(builder.parent_child_num_map, parent_items)
        self.assertDictEqual(builder.child_parent_num_map, child_item)
        self.assertTrue(builder.detect_parent_child_map_for_items())
