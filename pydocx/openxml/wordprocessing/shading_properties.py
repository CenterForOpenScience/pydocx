from __future__ import absolute_import, print_function, unicode_literals

from pydocx.models import XmlModel, XmlAttribute


class BaseShading(XmlModel):
    pattern = XmlAttribute(name='val')
    color = XmlAttribute(name='color')
    fill = XmlAttribute(name='fill')

    @property
    def background_color(self):
        """Get the background color for shading. Note that this is a simple
        implementation as we can't translate all the shadings into CSS"""

        color = None

        if self.pattern in ('solid',) and self.color:
            if self.color in ('auto',):
                # By default we set the color to black if auto is specified
                color = '000000'
            else:
                color = self.color
        elif self.fill and self.fill not in ('auto',):
            color = self.fill
        elif self.color not in ('auto',):
            color = self.color

        return color

    @classmethod
    def attributes_list(cls, obj):
        if obj is not None:
            return (obj.pattern,
                    obj.color,
                    obj.fill)

    def __eq__(self, other):
        return self.attributes_list(self) == self.attributes_list(other)

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return any(self.attributes_list(self) or [None])


class ParagraphShading(BaseShading):
    XML_TAG = 'shd'


class RunShading(BaseShading):
    XML_TAG = 'shd'
