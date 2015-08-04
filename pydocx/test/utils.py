from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import posixpath
import re
import os.path
from io import BytesIO
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from pydocx.packaging import PackageRelationship, ZipPackagePart
from pydocx.export.html import PyDocXHTMLExporter
from pydocx.openxml.packaging import (
    FootnotesPart,
    MainDocumentPart,
    NumberingDefinitionsPart,
    StyleDefinitionsPart,
    WordprocessingDocument,
)

from pydocx.test.document_builder import DocxBuilder as DXB


def prettify(xml_string):
    """Return a pretty-printed XML string for the Element.
    """
    parsed = minidom.parseString(xml_string)
    return parsed.toprettyxml(indent='\t')


def html_is_equal(a, b):
    a = collapse_html(a)
    b = collapse_html(b)
    return a == b


def assert_html_equal(actual_html, expected_html, filename=None):
    if not html_is_equal(actual_html, expected_html):
        try:
            html = prettify(actual_html)
        except ExpatError:
            html = actual_html
        if filename:
            with open('tests/failures/%s.html' % filename, 'w') as f:
                f.write(html)
        raise AssertionError(html)


def collapse_html(html):
    """
    Remove insignificant whitespace from the html.

    >>> print(collapse_html('''\\
    ...     <h1>
    ...         Heading
    ...     </h1>
    ... '''))
    <h1>Heading</h1>
    >>> print(collapse_html('''\\
    ...     <p>
    ...         Paragraph with
    ...         multiple lines.
    ...     </p>
    ... '''))
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


class PyDocXHTMLExporterNoStyle(PyDocXHTMLExporter):
    def style(self):
        return ''


class WordprocessingDocumentFactory(object):
    PARTS_TO_PATHS = {
        FootnotesPart: 'word/footnotes.xml',
        MainDocumentPart: 'word/document.xml',
        StyleDefinitionsPart: 'word/styles.xml',
        NumberingDefinitionsPart: 'word/numbering.xml',
    }

    PARTS_TO_PREPARE_CONTENT_FUNCS = {
        FootnotesPart: 'prepare_footnotes_content',
        MainDocumentPart: 'prepare_main_document_content',
        StyleDefinitionsPart: 'prepare_style_content',
        NumberingDefinitionsPart: 'prepare_numbering_content',
    }

    relationship_format = '''
        <Relationship Id="{id}" Type="{type}" Target="{target}" TargetMode="{target_mode}"/>
    '''  # noqa

    content_types = '''
        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
          <Override PartName="/_rels/.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
          <Override PartName="/word/_rels/document.xml.rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
          <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
        </Types>
    '''  # noqa

    def __init__(self, items=None, xml_header=None):
        self.items = items
        if not self.items:
            self.items = {}

        if xml_header is None:
            xml_header = '<?xml version="1.0" encoding="UTF-8"?>'
        self.xml_header = xml_header

    def to_zip_dict(self):
        '''
        Return a dictionary that can be passed to ``create_zip_archive``
        The keys specify paths within the zip archive, and the values specify
        the data at that path.
        '''

        zip_dict = {}
        part_class_to_uri = {}

        for item_class, (content, rels) in self.items.items():
            uri = self.PARTS_TO_PATHS[item_class]
            part_class_to_uri[item_class] = uri
            zip_dict[uri] = content
            if rels:
                rels_uri = ZipPackagePart.get_relationship_part_uri(uri)
                zip_dict[rels_uri] = rels

        base_uri, base_content = self.get_base_relationships(part_class_to_uri)
        zip_dict[base_uri] = base_content

        content_types_uri, content_types = self.get_content_types()
        zip_dict[content_types_uri] = content_types

        return zip_dict

    def add(self, item_part_class, content, relationships=None):
        '''
        Add an item of type `item_part_class` to the document with content
        `content`. Optionally, you can specify the `relationships` this item
        has.

        For example:

            document = WordprocessingDocumentFactory()
            document.add(MainDocumentPart, '<p>Foo</p>')

        Internal relationships are managed automatically by adding the items
        which are children before adding the parent:

            document = WordprocessingDocumentFactory()
            document.add(StyleDefinitionsPart, '<style>...</style>')
            document.add(MainDocumentPart, '<p>Foo</p>')

        In the above example, the MainDocumentPart item will automatically
        acquire the StyleDefinitionsPart as a child item.

        For external relationships, you can pass them in directly:

            document = WordprocessingDocumentFactory()
            document_rels = document.relationship_format.format(
                id='foobar',
                type=ImagePart.relationship_type,
                target='http://google.com/logo.gif',
                target_mode='External',
            )
            document.add(MainDocumentPart, '<p>Foo</p>', document_rels)

        The external relationships will be combined with any automatic
        relationships that existed.
        '''
        func_name = self.PARTS_TO_PREPARE_CONTENT_FUNCS.get(item_part_class)
        func = getattr(self, func_name)
        if callable(func):
            content = func(content)
        relationships = self.prepare_relationship_data(
            content=relationships,
            item_part_class=item_part_class,
        )
        self.items[item_part_class] = (content, relationships)

    def prepare_xml_content(self, xml):
        return '{header}{xml}'.format(header=self.xml_header, xml=xml)

    def prepare_relationship_data(self, content, item_part_class=None):
        if item_part_class:
            # Automatically build relationships based on the defined child
            # types and previously added parts to this factory
            relevant_part_classes = (
                set(item_part_class.child_part_types) & set(self.items.keys())
            )
            automatic_rels = ''.join(self.build_relationship_content(dict(
                (
                    part_class,
                    self.get_part_name(item_part_class, part_class),
                )
                for part_class in relevant_part_classes
            )))
            if content:
                content = content + automatic_rels
            else:
                content = automatic_rels
        xml = '<Relationships xmlns="{ns}">{rels}</Relationships>'.format(
            ns=PackageRelationship.namespace,
            rels=content,
        )
        return self.prepare_xml_content(xml=xml)

    def get_part_name(self, parent_part_class, part_class):
        parent_uri = self.PARTS_TO_PATHS[parent_part_class]
        uri = self.PARTS_TO_PATHS[part_class]
        return os.path.relpath(uri, os.path.dirname(parent_uri))

    def get_base_relationships(self, part_class_to_uri):
        uri = ZipPackagePart.get_relationship_part_uri('')
        content = ''.join(self.build_relationship_content(part_class_to_uri))
        content = self.prepare_relationship_data(content=content)
        return uri, content

    def build_relationship_content(self, part_class_to_uri):
        for rid, (part_class, uri) in enumerate(part_class_to_uri.items()):
            yield self.relationship_format.format(
                id='rId{rid}'.format(rid=rid),
                type=part_class.relationship_type,
                target=uri,
                target_mode='Internal',
            )

    def prepare_main_document_content(self, xml):
        xml = '<document><body>{xml}</body></document>'.format(xml=xml)
        return self.prepare_xml_content(xml=xml)

    def prepare_style_content(self, xml):
        xml = '<styles>{xml}</styles>'.format(xml=xml)
        return self.prepare_xml_content(xml=xml)

    def prepare_footnotes_content(self, xml):
        xml = '<footnotes>{xml}</footnotes>'.format(xml=xml)
        return self.prepare_xml_content(xml=xml)

    def prepare_numbering_content(self, xml):
        xml = '<numbering>{xml}</numbering>'.format(xml=xml)
        return self.prepare_xml_content(xml=xml)

    def get_content_types(self):
        content_types = self.prepare_xml_content(xml=self.content_types)
        return '[Content_Types].xml', content_types


class XMLDocx2Html(PyDocXHTMLExporter):
    """
    Create the object without passing in a path to the document, set them
    manually.
    """
    def __init__(self, *args, **kwargs):
        # Pass in nothing for the path
        self.document_xml = kwargs.pop('document_xml')
        self.relationships = kwargs.pop('relationships') or []
        self.numbering_dict = kwargs.pop('numbering_dict', None) or {}
        self.styles_xml = kwargs.pop('styles_xml', '')
        super(XMLDocx2Html, self).__init__(path=None, *args, **kwargs)

    def load_document(self):
        # It's likely that we could replace this logic with a
        # WordprocessingDocumentFactory
        document = WordprocessingDocument(path=None)
        package = document.package
        document_part = package.create_part(
            uri='/word/document.xml',
        )

        if self.numbering_dict is not None:
            numbering_xml = DXB.numbering(self.numbering_dict)
            self.relationships.append({
                'external': False,
                'target_path': 'numbering.xml',
                'data': numbering_xml,
                'relationship_id': 'numbering',
                'relationship_type': NumberingDefinitionsPart.relationship_type,  # noqa
            })

        if self.styles_xml:
            self.relationships.append({
                'external': False,
                'target_path': 'styles.xml',
                'data': self.styles_xml,
                'relationship_id': 'styles',
                'relationship_type': StyleDefinitionsPart.relationship_type,
            })

        for relationship in self.relationships:
            target_mode = 'Internal'
            if relationship['external']:
                target_mode = 'External'
            target_uri = relationship['target_path']
            if 'data' in relationship:
                full_target_uri = posixpath.join(
                    package.uri,
                    'word',
                    target_uri,
                )
                package.streams[full_target_uri] = BytesIO(
                    relationship['data'],
                )
                package.create_part(uri=full_target_uri)
            document_part.create_relationship(
                target_uri=target_uri,
                target_mode=target_mode,
                relationship_type=relationship['relationship_type'],
                relationship_id=relationship['relationship_id'],
            )

        package.streams[document_part.uri] = BytesIO(self.document_xml)
        package.create_relationship(
            target_uri=document_part.uri,
            target_mode='Internal',
            relationship_type=MainDocumentPart.relationship_type,
        )

        # This is the standard page width for a word document (in points), Also
        # the page width that we are looking for in the test.
        self._page_width = 612

        return document
