# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from unittest import TestCase

from pydocx.export.numbering_span import NumberingSpanBuilder
from pydocx.openxml.wordprocessing import (
    Break,
    Paragraph,
    Run,
    TabChar,
    Text,
)


class NumberingSpanTestBase(TestCase):
    def setUp(self):
        self.builder = NumberingSpanBuilder()


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
