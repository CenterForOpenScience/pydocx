# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from pydocx.openxml import wordprocessing


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


class NumberingSpanBuilder(object):
    '''
    De-flatten a list of OOXML components into a list of NumberingSpan + Items by calling
    `get_numbering_spans`

    In OOXML, several components can hold paragraphs. For example, the Body and
    TableCell components. Some of these paragraphs may define numbering
    information. The numbering structure is nested, but the list of paragraphs
    is flat. The purpose of this builder class is to convert the flattened
    list of paragraphs + paragraphs with numbering definitions + other misc
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
        num_def = paragraph.get_numbering_definition()
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
        num_def = paragraph.get_numbering_definition()
        return num_def == self.current_span.numbering_definition

    def handle_start_new_span(self, index, paragraph):
        num_def = paragraph.get_numbering_definition()
        level = paragraph.get_numbering_level()

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
        num_def = paragraph.get_numbering_definition()
        level = paragraph.get_numbering_level()

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
            self.candidate_numbering_items = []
            self.current_item_index = index
            return

        num_def = paragraph.get_numbering_definition()
        level = paragraph.get_numbering_level()

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
