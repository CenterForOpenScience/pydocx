from __future__ import absolute_import, print_function, unicode_literals

from pydocx.models import XmlModel, XmlChild, XmlAttribute
from pydocx.types import OnOff

BORDERS_CSS_DEFAULT = 'solid'
BORDERS_CSS_MAPPING = {
    'none': 'none',
    'single': 'solid',
    'double': 'double',
    'triple': 'double',
    'dotted': 'dotted',
    'dashed': 'dashed',
    'dashSmallGap': 'dashed',
    'dotDash': 'dashed',
    'dotDotDash': 'dashed',
    'outset': 'outset'
}


class BaseBorder(XmlModel):
    style = XmlAttribute(name='val')
    width = XmlAttribute(name='sz')
    _color = XmlAttribute(name='color')
    space = XmlAttribute(name='space')
    shadow = XmlAttribute(type=OnOff, name='shadow')

    @property
    def color(self):
        if self._color in ('auto',):
            self._color = '000000'
        return self._color

    @property
    def css_style(self):
        if self.style:
            return BORDERS_CSS_MAPPING.get(self.style, BORDERS_CSS_DEFAULT)
        return BORDERS_CSS_DEFAULT

    @property
    def width_points(self):
        """width is of type ST_EighthPointMeasure"""

        if self.width:
            width = int(self.width) / 8.0
            if self.style in ('double',):
                width *= 3
            elif self.style in ('triple',):
                width *= 5
            width = float('%.1f' % width)
        else:
            width = 1

        return width

    @property
    def spacing(self):
        if self.space:
            return self.space
        # If space is not defined we assume 0 by default
        return '0'

    def get_css_border_style(self, to_str=True):
        border_style = [
            # border-width
            '%spt' % self.width_points,
            # border-style
            self.css_style,
            # border-color
            '#%s' % self.color
        ]
        if to_str:
            border_style = ' '.join(border_style)
        return border_style

    @classmethod
    def attributes_list(cls, obj):
        if obj:
            return (obj.css_style,
                    obj.width,
                    obj.color,
                    obj.spacing,
                    obj.shadow)

    def __eq__(self, other):
        return self.attributes_list(self) == self.attributes_list(other)

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        if self.style and self.style in ['nil', 'none']:
            return False
        return True


class TopBorder(BaseBorder):
    XML_TAG = 'top'


class LeftBorder(BaseBorder):
    XML_TAG = 'left'


class BottomBorder(BaseBorder):
    XML_TAG = 'bottom'


class RightBorder(BaseBorder):
    XML_TAG = 'right'


class BetweenBorder(BaseBorder):
    XML_TAG = 'between'


class BaseBorderStyle(object):
    def get_border_style(self):
        raise NotImplemented

    def get_shadow_style(self):
        raise NotImplemented

    def get_padding_style(self):
        raise NotImplemented


class ParagraphBorders(XmlModel, BaseBorderStyle):
    XML_TAG = 'pBdr'
    top = XmlChild(type=TopBorder)
    left = XmlChild(type=LeftBorder)
    bottom = XmlChild(type=BottomBorder)
    right = XmlChild(type=RightBorder)
    between = XmlChild(type=BetweenBorder)

    @property
    def borders_name(self):
        """Borders are listed by how CSS is expecting them to be"""

        return 'top', 'right', 'bottom', 'left'

    @property
    def all_borders(self):
        return list(map(lambda brd_name: getattr(self, brd_name), self.borders_name))

    def get_borders_attribute(self, attr_name, default=None, to_type=None):
        attributes = list(map(lambda brd: getattr(brd, attr_name, default), self.all_borders))
        if to_type is not None:
            if to_type is set:
                attributes = set(attributes)
            else:
                attributes = list(map(to_type, attributes))

        return attributes

    def borders_have_same_properties(self):
        if not any(self.all_borders):
            return False

        color = self.get_borders_attribute('color', to_type=set)
        style = self.get_borders_attribute('style', to_type=set)
        width = self.get_borders_attribute('width', to_type=set)

        if list(set(map(len, (color, style, width)))) == [1]:
            return True

        return False

    def get_border_style(self):
        border_styles = {}
        if self.borders_have_same_properties():
            border_styles['border'] = self.top.get_css_border_style()
        else:
            for border_name, border in zip(self.borders_name, self.all_borders):
                if border:
                    border_styles['border-%s' % border_name] = border.get_css_border_style()

        return border_styles

    def get_between_border_style(self):
        border_styles = {}
        if self.between:
            border_styles['border-top'] = self.between.get_css_border_style()

        # Because there can be padding added by the parent border we need to make sure that
        # we adapt margins to not have extra space on left/right
        margins = [
            # top
            self.between.spacing,
            # right
            '%s' % -int(getattr(self.right, 'spacing', 0)),
            # bottom
            self.between.spacing,
            # left
            '%s' % -int(getattr(self.left, 'spacing', 0))
        ]

        border_styles['margin'] = ' '.join(map(lambda x: '%spt' % x, margins))
        return border_styles

    def get_padding_style(self):
        padding_styles = {}
        padding = self.get_borders_attribute('spacing', default=0, to_type=str)
        if len(set(padding)) == 1:
            padding = list(set(padding))
        padding_styles['padding'] = ' '.join(map(lambda x: '%spt' % x, padding))
        return padding_styles

    def get_shadow_style(self):
        shadow_styles = {}
        border = self.top
        if border and bool(border.shadow):
            shadow_styles['box-shadow'] = '{0}pt {0}pt'.format(border.width_points)
        return shadow_styles

    @classmethod
    def attributes_list(cls, obj):
        if obj is not None:
            return (obj.top,
                    obj.left,
                    obj.bottom,
                    obj.right,
                    obj.between)

    def __eq__(self, other):
        return self.attributes_list(self) == self.attributes_list(other)

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        return any(self.attributes_list(self) or [None])


class RunBorders(BaseBorder, BaseBorderStyle):
    XML_TAG = 'bdr'

    def get_border_style(self):
        border_styles = {'border': self.get_css_border_style()}
        return border_styles

    def get_shadow_style(self):
        shadow_styles = {}
        if bool(self.shadow):
            shadow_styles['box-shadow'] = '{0}pt {0}pt'.format(self.width_points)
        return shadow_styles

    def get_padding_style(self):
        padding_styles = {}
        # if spacing is 0 no need to set the padding
        if int(self.spacing):
            padding_styles['padding'] = '%spt' % self.spacing
        return padding_styles
