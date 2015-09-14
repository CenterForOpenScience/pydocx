# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import base64

from pydocx.constants import EMUS_PER_PIXEL
from pydocx.openxml.packaging import ImagePart, MainDocumentPart
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class DrawingGraphicBlipTestCase(DocumentGeneratorTestCase):
    def test_inline_image_with_multiple_ext_definitions(self):
        # Ensure that the image size can be calculated correctly even if the
        # image size ext isn't the first ext in the drawing node
        width_px = 5
        height_px = 10

        document_xml = '''
            <p>
            <r>
              <t>Foo</t>
              <drawing>
                <inline>
                  <graphic>
                    <graphicData>
                      <pic>
                        <blipFill>
                          <blip embed="foobar">
                            <extLst>
                              <ext/>
                            </extLst>
                          </blip>
                        </blipFill>
                        <spPr>
                          <xfrm>
                            <ext cx="{cx}" cy="{cy}"/>
                          </xfrm>
                        </spPr>
                      </pic>
                    </graphicData>
                  </graphic>
                </inline>
              </drawing>
              <t>Bar</t>
            </r>
            </p>
        '''.format(
            cx=width_px * EMUS_PER_PIXEL,
            cy=height_px * EMUS_PER_PIXEL,
        )

        document = WordprocessingDocumentFactory()
        image_url = 'http://google.com/image1.gif'
        document_rels = document.relationship_format.format(
            id='foobar',
            type=ImagePart.relationship_type,
            target=image_url,
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '''
            <p>
              Foo
              <img
                height="{height}px"
                src="http://google.com/image1.gif"
                width="{width}px"
              />
              Bar
            </p>
        '''.format(width=width_px, height=height_px)

        self.assert_document_generates_html(document, expected_html)

    def test_anchor_with_multiple_ext_definitions(self):
        width_px = 5
        height_px = 10

        # Ensure that the image size can be calculated correctly even if the
        # image size ext isn't the first ext in the drawing node
        document_xml = '''
            <p>
            <r>
              <t>Foo</t>
              <drawing>
                <anchor>
                  <graphic>
                    <graphicData>
                      <pic>
                        <blipFill>
                          <blip embed="foobar">
                            <extLst>
                              <ext/>
                            </extLst>
                          </blip>
                        </blipFill>
                        <spPr>
                          <xfrm>
                            <ext cx="{cx}" cy="{cy}"/>
                          </xfrm>
                        </spPr>
                      </pic>
                    </graphicData>
                  </graphic>
                </anchor>
              </drawing>
              <t>Bar</t>
            </r>
            </p>
        '''.format(
            cx=width_px * EMUS_PER_PIXEL,
            cy=height_px * EMUS_PER_PIXEL,
        )

        document = WordprocessingDocumentFactory()
        image_url = 'http://google.com/image1.gif'
        document_rels = document.relationship_format.format(
            id='foobar',
            type=ImagePart.relationship_type,
            target=image_url,
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '''
            <p>
              Foo
              <img
                height="{height}px"
                src="http://google.com/image1.gif"
                width="{width}px"
              />
              Bar
            </p>
        '''.format(width=width_px, height=height_px)

        self.assert_document_generates_html(document, expected_html)

    def test_anchor_with_no_size_ext(self):
        # Ensure the image html is still rendered even if the size cannot be
        # calculated
        document_xml = '''
            <p>
            <r>
              <t>Foo</t>
              <drawing>
                <anchor>
                  <graphic>
                    <graphicData>
                      <pic>
                        <blipFill>
                          <blip embed="foobar"/>
                        </blipFill>
                        <spPr>
                          <xfrm/>
                        </spPr>
                      </pic>
                    </graphicData>
                  </graphic>
                </anchor>
              </drawing>
              <t>Bar</t>
            </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        image_url = 'http://google.com/image1.gif'
        document_rels = document.relationship_format.format(
            id='foobar',
            type=ImagePart.relationship_type,
            target=image_url,
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '''
            <p>
              Foo
              <img src="http://google.com/image1.gif" />
              Bar
            </p>
        '''

        self.assert_document_generates_html(document, expected_html)

    def test_blip_embed_refers_to_undefined_image_relationship(self):
        # Ensure that if a blip embed refers to an undefined image
        # relationshipp, the image rendering is skipped
        document_xml = '''
            <p>
            <r>
              <t>Foo</t>
              <drawing>
                <anchor>
                  <graphic>
                    <graphicData>
                      <pic>
                        <blipFill>
                          <blip embed="foobar" />
                        </blipFill>
                      </pic>
                    </graphicData>
                  </graphic>
                </anchor>
              </drawing>
              <t>Bar</t>
            </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>FooBar</p>'

        self.assert_document_generates_html(document, expected_html)

    def test_internal_image_is_included_with_base64_content(self):
        width_px = 5
        height_px = 10

        document_xml = '''
            <p>
            <r>
              <t>Foo</t>
              <drawing>
                <anchor>
                  <graphic>
                    <graphicData>
                      <pic>
                        <blipFill>
                          <blip embed="foobar" />
                        </blipFill>
                        <spPr>
                          <xfrm>
                            <ext cx="{cx}" cy="{cy}"/>
                          </xfrm>
                        </spPr>
                      </pic>
                    </graphicData>
                  </graphic>
                </anchor>
              </drawing>
              <t>Bar</t>
            </r>
            </p>
        '''.format(
            cx=width_px * EMUS_PER_PIXEL,
            cy=height_px * EMUS_PER_PIXEL,
        )

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type=ImagePart.relationship_type,
            target='media/image1.jpeg',
            target_mode='Internal',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        image_data = 'fake data'

        expected_html = '''
            <p>
              Foo
              <img
                height="{height}px"
                src="data:image/jpeg;base64,{data}"
                width="{width}px"
              />
              Bar
            </p>
        '''.format(
            width=width_px,
            height=height_px,
            # This is kind of weird, needed otherwise python 3.3 breaks
            data=base64.b64encode(image_data.encode('utf-8')).decode('utf-8'),
        )

        self.assert_document_generates_html(
            document,
            expected_html,
            additional_parts={
                'word/media/image1.jpeg': image_data,
            },
        )

    def test_internal_image_is_not_included_if_part_is_missing(self):
        width_px = 5
        height_px = 10

        document_xml = '''
            <p>
            <r>
              <t>Foo</t>
              <drawing>
                <anchor>
                  <graphic>
                    <graphicData>
                      <pic>
                        <blipFill>
                          <blip embed="foobar" />
                        </blipFill>
                        <spPr>
                          <xfrm>
                            <ext cx="{cx}" cy="{cy}"/>
                          </xfrm>
                        </spPr>
                      </pic>
                    </graphicData>
                  </graphic>
                </anchor>
              </drawing>
              <t>Bar</t>
            </r>
            </p>
        '''.format(
            cx=width_px * EMUS_PER_PIXEL,
            cy=height_px * EMUS_PER_PIXEL,
        )

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type=ImagePart.relationship_type,
            target='media/image1.jpeg',
            target_mode='Internal',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '<p>FooBar</p>'

        self.assert_document_generates_html(
            document,
            expected_html,
            additional_parts={
                # Purposefully commented out
                # 'word/media/image1.jpeg': '',
            },
        )
