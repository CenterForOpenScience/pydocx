# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from itertools import chain

from pydocx.util.xml import convert_dictionary_to_html_attributes


def is_only_whitespace(obj):
    '''
    If the obj has `strip` return True if calling strip on the obj results in
    an empty instance. Otherwise, return False.
    '''
    if hasattr(obj, 'strip'):
        return not obj.strip()
    return False


def is_not_empty_and_not_only_whitespace(gen):
    '''
    Determine if a generator is empty, or consists only of whitespace.

    If the generator is non-empty, return the original generator. Otherwise,
    return None
    '''
    queue = []
    if gen is None:
        return
    try:
        for item in gen:
            queue.append(item)
            is_whitespace = True
            if isinstance(item, HtmlTag):
                # If we encounter a tag that allows whitespace, then we can stop
                is_whitespace = not item.allow_whitespace
            else:
                is_whitespace = is_only_whitespace(item)

            if not is_whitespace:
                # This item isn't whitespace, so we're done scanning
                return chain(queue, gen)

    except StopIteration:
        pass


class HtmlTag(object):
    closed_tag_format = '</{tag}>'

    def __init__(
            self,
            tag,
            allow_self_closing=False,
            closed=False,
            allow_whitespace=False,
            **attrs
    ):
        self.tag = tag
        self.allow_self_closing = allow_self_closing
        self.attrs = attrs
        self.closed = closed
        self.allow_whitespace = allow_whitespace

    def apply(self, results, allow_empty=True):
        if not allow_empty:
            results = is_not_empty_and_not_only_whitespace(results)
            if results is None:
                return

        sequence = [[self]]
        if results is not None:
            sequence.append(results)

        if not self.allow_self_closing:
            sequence.append([self.close()])

        results = chain(*sequence)

        for result in results:
            yield result

    def close(self):
        return HtmlTag(
            tag=self.tag,
            closed=True,
        )

    def to_html(self):
        if self.closed is True:
            return self.closed_tag_format.format(tag=self.tag)
        else:
            attrs = self.get_html_attrs()
            end_bracket = '>'
            if self.allow_self_closing:
                end_bracket = ' />'
            if attrs:
                return '<{tag} {attrs}{end}'.format(
                    tag=self.tag,
                    attrs=attrs,
                    end=end_bracket,
                )
            else:
                return '<{tag}{end}'.format(tag=self.tag, end=end_bracket)

    def get_html_attrs(self):
        return convert_dictionary_to_html_attributes(self.attrs)
