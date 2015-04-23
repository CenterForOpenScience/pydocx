# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.models import XmlModel, XmlCollection, XmlChild, XmlAttribute
from pydocx.util.xml import parse_xml_from_string


class AppleModel(XmlModel):
    type = XmlAttribute(default='Honey Crisp')


class OrangeModel(XmlModel):
    type = XmlAttribute(default='Organic')


class ItemsModel(XmlModel):
    items = XmlCollection({
        'apple': AppleModel,
        'orange': OrangeModel,
    })


class BucketModel(XmlModel):
    items = XmlChild(type=ItemsModel)


class BaseTestCase(TestCase):
    def _get_model_instance_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return self.model.load(root)


class XmlChildTestCase(BaseTestCase):
    model = BucketModel

    def test_items_None_if_not_present(self):
        xml = '<bucket />'
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.items, None)


class XmlCollectionTestCase(BaseTestCase):
    model = BucketModel

    def test_items_items_empty_if_no_items_present(self):
        xml = '''
            <bucket>
                <items>
                </items>
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.items.items, [])
