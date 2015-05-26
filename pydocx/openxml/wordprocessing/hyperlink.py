# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlAttribute, XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run


class Hyperlink(XmlModel):
    XML_TAG = 'hyperlink'

    hyperlink_id = XmlAttribute(name='id')
    children = XmlCollection(
        Run,
    )

    def get_target_uri(self, part):
        package_part = part.package_part
        try:
            relationship = package_part.get_relationship(
                relationship_id=self.hyperlink_id,
            )
        except KeyError:
            return None
        return relationship.target_uri
