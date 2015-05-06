from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict

from pydocx.constants import (
    UPPER_ROMAN_TO_HEADING_VALUE,
    TAGS_HOLDING_CONTENT_TAGS,
    TAGS_CONTAINING_CONTENT,
)
from pydocx.util.memoize import MultiMemoizeMixin
from pydocx.util.xml import (
    filter_children,
    find_all,
    find_ancestor_with_tag,
    get_list_style,
    has_descendant_with_tag,
)


class NamespacedNumId(object):
    def __init__(self, num_id, num_tables, *args, **kwargs):
        self._num_id = num_id
        self._num_tables = num_tables

    def __unicode__(self, *args, **kwargs):
        return '%s:%d' % (
            self._num_id,
            self._num_tables,
        )

    def __str__(self, *args, **kwargs):
        return self.__unicode__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self.__unicode__(*args, **kwargs)

    def __eq__(self, other):
        if other is None:
            return False
        return repr(self) == repr(other)

    def __ne__(self, other):
        if other is None:
            return False
        return repr(self) != repr(other)

    @property
    def num_id(self):
        return self._num_id

    def __hash__(self):
        return id(str(self))


class PydocxPreProcessor(MultiMemoizeMixin):
    def __init__(self, numbering_root=None, *args, **kwargs):
        self.meta_data = defaultdict(dict)
        self.numbering_root = numbering_root

    def perform_pre_processing(self, root, *args, **kwargs):
        self._add_parent(root)
        # If we don't have a numbering root there cannot be any lists.
        if self.numbering_root is not None:
            self._set_list_attributes(root)
        self._set_table_attributes(root)
        self._set_is_in_table(root)

        body = root.find('./body')
        self._set_next(body)
        p_elements = [
            child for child in find_all(body, 'p')
        ]
        list_elements = [
            child for child in p_elements
            if self.is_list_item(child)
        ]
        # Find the first and last li elements
        num_ids = set([self.num_id(i) for i in list_elements])
        ilvls = set([self.ilvl(i) for i in list_elements])
        self._set_first_list_item(num_ids, ilvls, list_elements)
        self._set_last_list_item(num_ids, list_elements)

    def is_first_list_item(self, el):
        return self.meta_data[el].get('is_first_list_item', False)

    def is_last_list_item_in_root(self, el):
        return self.meta_data[el].get('is_last_list_item_in_root', False)

    def is_list_item(self, el):
        return self.meta_data[el].get('is_list_item', False)

    def num_id(self, el):
        if not self.is_list_item(el):
            return None
        return self.meta_data[el].get('num_id')

    def ilvl(self, el):
        if not self.is_list_item(el):
            return None
        return self.meta_data[el].get('ilvl')

    def heading_level(self, el):
        return self.meta_data[el].get('heading_level')

    def is_in_table(self, el):
        return self.meta_data[el].get('is_in_table')

    def row_index(self, el):
        return self.meta_data[el].get('row_index')

    def column_index(self, el):
        return self.meta_data[el].get('column_index')

    def vmerge_continue(self, el):
        return self.meta_data[el].get('vmerge_continue')

    def next(self, el):
        if el not in self.meta_data:
            return
        return self.meta_data[el].get('next')

    def previous(self, el):
        if el not in self.meta_data:
            return
        return self.meta_data[el].get('previous')

    def parent(self, el):
        return self.meta_data[el].get('parent')

    def _add_parent(self, el):  # if a parent, make that an attribute
        for child in el.getchildren():
            self.meta_data[child]['parent'] = el
            self._add_parent(child)

    def _set_list_attributes(self, el):
        list_elements = find_all(el, 'numId')
        for li in list_elements:
            parent = find_ancestor_with_tag(self, li, 'p')
            # Deleted text in a list will have a numId but no ilvl.
            if parent is None:
                continue
            parent_ilvl = parent.find('./pPr/numPr/ilvl')
            if parent_ilvl is None:
                continue
            self.meta_data[parent]['is_list_item'] = True
            self.meta_data[parent]['num_id'] = self._generate_num_id(parent)
            self.meta_data[parent]['ilvl'] = parent_ilvl.attrib['val']

    def _generate_num_id(self, el):
        '''
        Fun fact: It is possible to have a list in the root, that holds a table
        that holds a list and for both lists to have the same numId. When this
        happens we should namespace the nested list with the number of tables
        it is in to ensure it is considered a new list. Otherwise all sorts of
        terrible html gets generated.
        '''
        el_num_id = el.find('./pPr/numPr/numId')
        num_id = el_num_id.attrib['val']

        # First, go up the parent until we get None and count the number of
        # tables there are.
        num_tables = 0
        while self.parent(el) is not None:
            if el.tag == 'tbl':
                num_tables += 1
            el = self.parent(el)
        return NamespacedNumId(
            num_id=num_id,
            num_tables=num_tables,
        )

    def _set_first_list_item(self, num_ids, ilvls, list_elements):
        # Lists are grouped by having the same `num_id` and `ilvl`. The first
        # list item is the first list item found for each `num_id` and `ilvl`
        # combination.
        if not ilvls:
            return
        lowest_ilvl = min(int(i) for i in ilvls)
        for num_id in num_ids:
            for ilvl in ilvls:
                filtered_list_elements = [
                    i for i in list_elements
                    if (
                        self.num_id(i) == num_id and
                        self.ilvl(i) == ilvl
                    )
                ]
                if not filtered_list_elements:
                    continue
                # The root list needs to be handled a little differently. We
                # only care about the first element in the root list.
                if int(ilvl) == lowest_ilvl:
                    filtered_list_elements = [filtered_list_elements[0]]

                first_one_marked = False
                for el in filtered_list_elements:
                    prev_el = self.previous(el)
                    if prev_el is None:
                        self.meta_data[el]['is_first_list_item'] = True

                    # If the current ilvl is greater than the previous then we
                    # are starting a new list.
                    if int(self.ilvl(prev_el) or 0) < int(self.ilvl(el)):
                        self.meta_data[el]['is_first_list_item'] = True
                    # The first list element in filtered_list_elements is
                    # always the first list item, no matter what.
                    if not first_one_marked:
                        self.meta_data[el]['is_first_list_item'] = True
                        first_one_marked = True

    def _set_last_list_item(self, num_ids, list_elements):
        # Find last list elements. Only mark list tags as the last list tag if
        # it is in the root of the document. This is only used to ensure that
        # once a root level list is finished we do not roll in the rest of the
        # non list elements into the first root level list.
        for num_id in num_ids:
            filtered_list_elements = [
                i for i in list_elements
                if self.num_id(i) == num_id
            ]
            if not filtered_list_elements:
                continue
            last_el = filtered_list_elements[-1]
            self.meta_data[last_el]['is_last_list_item_in_root'] = True

    def _set_table_attributes(self, el):
        tables = find_all(el, 'tbl')
        for table in tables:
            rows = filter_children(table, ['tr'])
            if rows is None:
                continue
            for i, row in enumerate(rows):
                tcs = filter_children(row, ['tc'])
                for j, child in enumerate(tcs):
                    self.meta_data[child]['row_index'] = i
                    self.meta_data[child]['column_index'] = j
                    v_merge = child.find('./tcPr/vMerge')
                    if (
                            v_merge is not None and
                            ('continue' == v_merge.get('val', '') or
                             v_merge.attrib == {})
                    ):
                        self.meta_data[child]['vmerge_continue'] = True

    def _set_is_in_table(self, el):
        paragraph_elements = find_all(el, 'p')
        for p in paragraph_elements:
            if find_ancestor_with_tag(self, p, 'tc') is not None:
                self.meta_data[p]['is_in_table'] = True

    def _set_next(self, body):
        def _get_children_with_content(el):
            # We only care about children if they have text in them.
            children = []
            for child in filter_children(el, TAGS_HOLDING_CONTENT_TAGS):
                _has_descendant_with_tag = any(
                    has_descendant_with_tag(child, tag) for
                    tag in TAGS_CONTAINING_CONTENT
                )
                if _has_descendant_with_tag:
                    children.append(child)
            return children

        def _assign_next(children):
            # Populate the `next` attribute for all the child elements.
            for i in range(len(children)):
                try:
                    if children[i + 1] is not None:
                        self.meta_data[children[i]]['next'] = children[i + 1]  # noqa
                except IndexError:
                    pass
                try:
                    if children[i - 1] is not None:
                        self.meta_data[children[i]]['previous'] = children[i - 1]  # noqa
                except IndexError:
                    pass
        # Assign next for everything in the root.
        _assign_next(_get_children_with_content(body))

        # In addition set next for everything in table cells.
        for tc in find_all(body, 'tc'):
            _assign_next(_get_children_with_content(tc))
