# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import string

from pydocx.openxml import wordprocessing
from pydocx.util.memoize import memoized

# Defined in 17.15.1.25
DEFAULT_AUTOMATIC_TAB_STOP_INTERVAL = 720  # twips


numeral_map = tuple(zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
))


def int_to_roman(i):
    '''
    Given any integer, return the roman numberal string.

    >>> int_to_roman(1)
    u'I'
    >>> int_to_roman(2)
    u'II'
    >>> int_to_roman(3)
    u'III'
    >>> int_to_roman(3789)
    u'MMMDCCLXXXIX'
    '''
    result = []
    for integer, numeral in numeral_map:
        count = i // integer
        result.append(numeral * count)
        i -= integer * count
    return ''.join(result)


def roman_to_int(n):
    '''
    Given a roman numberal string, return the decimal equivalent.

    >>> roman_to_int('I')
    1
    >>> roman_to_int('II')
    2
    >>> roman_to_int('III')
    3
    >>> roman_to_int('MMMDCCLXXXIX')
    3789
    '''
    i = result = 0
    for integer, numeral in numeral_map:
        while n[i:i + len(numeral)] == numeral:
            result += integer
            i += len(numeral)
    return result


def alpha_to_int(n):
    '''
    Given a ASCII lowercase base-26 string, return the decimal equivalent.

    >>> alpha_to_int('a')
    1
    >>> alpha_to_int('z')
    26
    >>> alpha_to_int('A')
    1
    >>> alpha_to_int('Z')
    26
    >>> alpha_to_int('aa')
    27
    >>> alpha_to_int('az')
    52
    >>> alpha_to_int('ba')
    53
    >>> alpha_to_int('bA')
    53
    >>> alpha_to_int('zz')
    702
    >>> alpha_to_int('zzz')
    18278
    '''
    result = 0
    for index, c in enumerate(reversed(n.lower())):
        ascii_index = string.ascii_lowercase.find(c)
        if ascii_index < 0:
            raise ValueError
        result += (ascii_index + 1) * len(string.ascii_lowercase) ** index
    return result


def int_to_alpha(i):
    '''
    Given any integer, return the equivalent base-26 ASCII lowercase string.

    >>> int_to_alpha(-1)
    u''
    >>> int_to_alpha(0)
    u''
    >>> int_to_alpha(1)
    u'a'
    >>> int_to_alpha(26)
    u'z'
    >>> int_to_alpha(27)
    u'aa'
    >>> int_to_alpha(52)  # (1 * 26 ^ 1) + (26 * 26 ^ 0)
    u'az'
    >>> int_to_alpha(53)  # (2 * 26 ^ 1) + (1 * 26 ^ 0)
    u'ba'
    >>> int_to_alpha(18278) # (26 * 26 ^ 2) + (26 * 26 ^ 1) + (26 * 26 ^ 0)
    u'zzz'
    '''
    result = []
    base = len(string.ascii_lowercase)
    while i >= 1:
        div, mod = divmod(i - 1, base)
        result.append(string.ascii_lowercase[mod])
        i = div
    return ''.join(reversed(result))


class NumberingSpan(object):
    '''
    This object contains a list of NumberingItems for which a particular
    NumberingLevel and NumberingDefinition are valid.
    '''

    def __init__(self, numbering_level, numbering_definition, parent):
        self.children = []
        self.numbering_level = numbering_level
        self.numbering_definition = numbering_definition
        self.parent = parent

    def append_child(self, child):
        assert isinstance(child, NumberingItem)
        self.children.append(child)

    def get_first_child_of_first_item(self):
        if not self.children:
            return
        first_item = self.children[0]
        if not first_item.children:
            return
        return first_item.children[0]


class NumberingItem(object):
    '''
    A container for NumberingSpans and any other type of item
    '''

    def __init__(self, numbering_span):
        self.numbering_span = numbering_span
        self.children = []

    @property
    def parent(self):
        return self.numbering_span

    def append_child(self, child):
        child.parent = self
        self.children.append(child)


class BaseNumberingSpanBuilder(object):
    '''
    De-flatten a list of OOXML components into a list of NumberingSpan + Items
    by calling `get_numbering_spans`

    In OOXML, several components can hold paragraphs. For example, the Body and
    TableCell components. Some of these paragraphs may define numbering
    information. The numbering structure is nested, but the list of paragraphs
    is flat. The purpose of this builder class is to convert the flattened list
    of paragraphs + paragraphs with numbering definitions + other misc
    components into nested hierarchical numbering structure. This is
    accomplished using the NumberingSpan and NumberingItem classes.
    '''

    def __init__(self, components):
        self.components = components
        self.numbering_span_stack = []
        self.current_span = None
        self.current_item = None
        self.current_item_index = 0
        self.candidate_numbering_items = []

    @memoized
    def get_numbering_level(self, paragraph):
        return paragraph.get_numbering_level()

    def include_candidate_items_in_current_item(self, new_item_index):
        '''
        A generator to determine which of the candidate numbering items need to
        be added to the current item and which need to be handled some other
        way.
        The list of candidate numbering items is reset when this function
        completes.
        '''
        if not self.current_item:
            return
        for index, item in self.candidate_numbering_items:
            if index < new_item_index:
                self.current_item.append_child(item)
            else:
                yield item
        # Since we've processed all of the candidate numbering items, reset it
        self.candidate_numbering_items = []

    def should_start_new_span(self, paragraph):
        '''
        If there's not a current span, and the paragraph is a heading
        style, do not start a new span.
        If there's not a current span, and the paragraph is NOT a heading
        style, then start a new span.
        If there is a current span, and the numbering definition
        of the paragraph is different than the numbering definition of the
        span, start a new span.
        Otherwise, do not start a new span.
        '''
        if self.current_span is None:
            return True
        level = self.get_numbering_level(paragraph)
        num_def = None
        if level:
            num_def = level.parent
        return num_def != self.current_span.numbering_definition

    def should_start_new_item(self, paragraph):
        '''
        If there is not a current span, do not start a new item.
        If the paragraph is a heading style, do not start a new item.
        Otherwise, only start a new item if the numbering definition of the
        paragraph matches the numbering definition of the current span.
        '''
        if self.current_span is None:
            return False
        level = self.get_numbering_level(paragraph)
        num_def = None
        if level:
            num_def = level.parent
        return num_def == self.current_span.numbering_definition

    def handle_start_new_span(self, index, paragraph):
        level = self.get_numbering_level(paragraph)
        num_def = level.parent

        if self.current_span:
            # We're starting a new span, but there's an existing span.
            # Yield back any candidates numbering items to be included
            # directly
            for _, item in self.candidate_numbering_items:
                yield item
            self.candidate_numbering_items = []

        self.current_span = NumberingSpan(
            numbering_level=level,
            numbering_definition=num_def,
            parent=paragraph.parent,
        )
        yield self.current_span

        self.numbering_span_stack = [self.current_span]

        self.current_item = NumberingItem(
            numbering_span=self.current_span,
        )
        self.current_item_index = index
        self.current_span.append_child(self.current_item)

    def handle_start_new_item(self, index, paragraph):
        level = self.get_numbering_level(paragraph)
        num_def = level.parent

        for item in self.include_candidate_items_in_current_item(index):
            # If an item gets yielded back here, it means it isn't being
            # added to the current item. Since it's not being added to the
            # current item, it gets added directly, outside of any
            # numbering span
            yield item

        if level == self.current_span.numbering_level:
            # The level hasn't changed
            self.current_item = NumberingItem(
                numbering_span=self.current_span,
            )
            self.current_item_index = index
            self.current_span.append_child(self.current_item)
        else:
            level_id = int(level.level_id)
            current_level_id = int(self.current_span.numbering_level.level_id)
            if level_id > current_level_id:
                # Add a new span + item to hold this new level
                next_numbering_span = NumberingSpan(
                    numbering_level=level,
                    numbering_definition=num_def,
                    parent=self.current_span,
                )
                self.numbering_span_stack.append(next_numbering_span)
                next_numbering_item = NumberingItem(
                    numbering_span=next_numbering_span,
                )
                next_numbering_span.children.append(next_numbering_item)
                self.current_item.append_child(next_numbering_span)
                self.current_span = next_numbering_span
                self.current_item = next_numbering_item
                self.current_item_index = index
            elif level_id < current_level_id:
                # we need to "subtract" a level. To do that, find the level
                # that we're going back to, which may not even exist
                previous_span = self.find_previous_numbering_span_with_lower_level(level_id)
                if self.numbering_span_stack:
                    assert previous_span
                    self.current_span = previous_span
                else:
                    # If the numbering_span_stack is empty now, it means
                    # we're handling a mangled level case
                    # For that scenario, create a new span
                    self.current_span = NumberingSpan(
                        numbering_level=level,
                        numbering_definition=num_def,
                        parent=self.current_span,
                    )
                    self.numbering_span_stack = [self.current_span]
                    yield self.current_span

                self.current_item = NumberingItem(
                    numbering_span=self.current_span,
                )
                self.current_item_index = index
                self.current_span.append_child(self.current_item)

    def find_previous_numbering_span_with_lower_level(self, level_id):
        previous_span = None
        while self.numbering_span_stack:
            previous_span = self.numbering_span_stack[-1]
            previous_level_id = int(previous_span.numbering_level.level_id)
            if previous_level_id <= level_id:
                # We may have found the level
                break
            self.numbering_span_stack.pop()
        return previous_span

    def handle_paragraph(self, index, paragraph):
        if paragraph.heading_style:
            # TODO Headings shouldn't break numbering. See #162
            # TODO not sure if reseting the stack is necessary or desired
            self.numbering_span_stack = []
            for _, item in self.candidate_numbering_items:
                yield item
            yield paragraph
            self.current_span = None
            self.current_item = None
            self.candidate_numbering_items = []
            self.current_item_index = index
            return

        level = self.get_numbering_level(paragraph)
        num_def = None
        if level:
            num_def = level.parent

        if num_def is None or level is None:
            if self.current_span is None:
                # This paragraph doesn't have any numbering information, and
                # there's no current numbering span, so we just yield it back
                yield paragraph
            else:
                # There is a current numbering span, but this paragraph doesn't
                # have any numbering information. Save the paragraph to a queue
                # for later processing. If a new item from the same span is
                # added, we'll re-add this paragraph to the current item.
                # Otherwise the paragraph will exist outside any numbering span
                self.candidate_numbering_items.append((index, paragraph))
            return

        start_new_span = self.should_start_new_span(paragraph)
        start_new_item = self.should_start_new_item(paragraph)

        if start_new_span:
            for item in self.handle_start_new_span(index, paragraph):
                yield item

        if start_new_item:
            for item in self.handle_start_new_item(index, paragraph):
                yield item

        if self.current_item:
            self.current_item.append_child(paragraph)
        else:
            yield paragraph

    def process_component(self, index, component):
        if isinstance(component, wordprocessing.Paragraph):
            for new_component in self.handle_paragraph(index, component):
                yield new_component
        elif self.current_item:
            self.candidate_numbering_items.append((index, component))
        else:
            yield component

    def get_numbering_spans(self):
        '''
        For each flattened numbering span defined in `self.components`, return
        a new list of items that is de-flattened.
        '''
        new_items = []
        index = 0

        for index, component in enumerate(self.components):
            new_items.extend(self.process_component(index, component))

        for item in self.include_candidate_items_in_current_item(self.current_item_index):
            new_items.append(item)

        return new_items


class FakeNumberingDetection(object):
    '''
    Detect paragraphs that visually look like numbering spans, and convert them
    into numbering spans.
    '''

    def __init__(self, *args, **kwargs):
        super(FakeNumberingDetection, self).__init__(*args, **kwargs)

        self.faked_list_patterns = [
            '{0}. ',
            '{0} ',
            '{0}) ',
            '({0}) ',
        ]

        self.faked_list_numbering_format_sequencer = {
            'decimal': lambda i: int(i),
            'upperRoman': lambda i: int_to_roman(i).upper(),
            'lowerRoman': lambda i: int_to_roman(i).lower(),
            'upperLetter': lambda i: int_to_alpha(i).upper(),
            'lowerLetter': lambda i: int_to_alpha(i).lower(),
        }

    @memoized
    def get_numbering_level(self, paragraph):
        return self.detect_faked_list(paragraph)

    def convert_tab_count_to_distance(self, tab_count):
        # TODO the full implementation of this is significantly more
        # complicated since we need to examine the custom tab stops, and also
        # the document's default tab stop.
        return tab_count * DEFAULT_AUTOMATIC_TAB_STOP_INTERVAL

    def text_is_a_faked_list(self, text, pattern, num_format, index):
        sequencer = self.faked_list_numbering_format_sequencer.get(num_format)
        if callable(sequencer):
            try:
                sequenced_index = sequencer(index)
            except ValueError:
                return False
            expected_text = pattern.format(sequenced_index)
            if text.startswith(expected_text):
                return expected_text
        return False

    def level_is_a_continuation_of_current_level(self, level, next_span_position):
        if not self.current_span:
            return False
        current_level = self.current_span.numbering_level
        if not level:
            return False
        if not level.start:
            return False
        if level.num_format != current_level.num_format:
            return False
        level_start = int(level.start)
        return level_start == next_span_position

    @memoized
    def get_left_position_for_paragraph(self, paragraph):
        tab_count = paragraph.get_number_of_initial_tabs()

        left_position = 0
        properties = paragraph.effective_properties
        if properties:
            properties = properties.start_margin_position

        # Add the tab distance
        tab_distance = self.convert_tab_count_to_distance(tab_count)
        left_position += tab_distance
        return left_position

    def detect_new_faked_level_started(self, paragraph, current_level_id=None):
        text = paragraph.get_text()

        level_id = 0
        if current_level_id is not None:
            level_id = current_level_id + 1

        next_span_position = 1
        for pattern in self.faked_list_patterns:
            for num_format in self.faked_list_numbering_format_sequencer:
                matching_text = self.text_is_a_faked_list(
                    text,
                    pattern,
                    num_format,
                    next_span_position,
                )
                if matching_text:
                    paragraph.strip_text_from_left(matching_text)
                    level = wordprocessing.Level(
                        level_id='{0}'.format(level_id),
                        num_format=num_format,
                    )
                    return level

    def get_left_position_for_numbering_span(self, numbering_span):
        paragraph = numbering_span.get_first_child_of_first_item()
        return self.get_left_position_for_paragraph(paragraph)

    def detect_faked_list(self, paragraph):
        level = paragraph.get_numbering_level()

        if self.current_span:
            current_level = self.current_span.numbering_level
            current_span_position = len(self.current_span.children)
            next_span_position = current_span_position + 1

            if self.level_is_a_continuation_of_current_level(level, next_span_position):
                return current_level
            elif level:
                return level

            text = paragraph.get_text()
            left_position = self.get_left_position_for_paragraph(paragraph)
            current_span_left_position = self.get_left_position_for_numbering_span(
                self.current_span,
            )
            if left_position > 0:
                paragraph.remove_initial_tabs()

            if left_position > current_span_left_position:
                new_faked_level = self.detect_new_faked_level_started(
                    paragraph,
                    int(current_level.level_id),
                )
                if new_faked_level:
                    current_level.parent.levels.append(new_faked_level)
                    new_faked_level.parent = current_level.parent
                    paragraph.remove_initial_tabs()
                    return new_faked_level
            elif left_position < current_span_left_position:
                previous_level = None
                for previous_span in reversed(self.numbering_span_stack[:-1]):
                    previous_span_left_pos = self.get_left_position_for_numbering_span(
                        previous_span,
                    )
                    if left_position == previous_span_left_pos:
                        previous_level = previous_span.numbering_level
                        break
                if previous_level:
                    previous_span_position = len(previous_span.children)
                    next_span_position = previous_span_position + 1
                    for pattern in self.faked_list_patterns:
                        matching_text = self.text_is_a_faked_list(
                            text,
                            pattern,
                            previous_level.num_format,
                            next_span_position,
                        )
                        if matching_text:
                            paragraph.strip_text_from_left(matching_text)
                            return previous_level

            elif left_position == current_span_left_position:
                for pattern in self.faked_list_patterns:
                    matching_text = self.text_is_a_faked_list(
                        text,
                        pattern,
                        current_level.num_format,
                        next_span_position,
                    )
                    if matching_text:
                        paragraph.strip_text_from_left(matching_text)
                        return current_level
        elif level:
            return level
        else:
            level = self.detect_new_faked_level_started(paragraph)
            if level:
                wordprocessing.AbstractNum(
                    levels=[level],
                )
                return level


class NumberingSpanBuilder(FakeNumberingDetection, BaseNumberingSpanBuilder):
    pass
