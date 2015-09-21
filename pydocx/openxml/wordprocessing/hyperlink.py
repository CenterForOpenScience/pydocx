# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlAttribute, XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run

from pydocx.util.memoize import memoized


class Hyperlink(XmlModel):
    XML_TAG = 'hyperlink'

    hyperlink_id = XmlAttribute(name='id')
    children = XmlCollection(
        Run,
    )

    @memoized
    def get_target_uri(self):
        if not self.container:
            return None
        if not self.container.package_part:
            return None
        package_part = self.container.package_part
        try:
            relationship = package_part.get_relationship(
                relationship_id=self.hyperlink_id,
            )
        except KeyError:
            return None
        return relationship.target_uri

    @property
    def target_uri(self):
        return self.get_target_uri()

    @target_uri.setter
    def target_uri(self, target_uri):
        self.get_target_uri.memo.set_cache(target_uri, self)
