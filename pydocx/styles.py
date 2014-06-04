from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict

from pydocx.types import OnOff


class XmlField(object):
    def __init__(self, name=None, default=None, type=None):
        self.name = name
        self.default = default
        self.type = type


class Attribute(XmlField):
    pass


class ChildTag(XmlField):
    def __init__(self, name=None, default=None, type=None, attrname=None):
        super(ChildTag, self).__init__(
            name=name,
            default=default,
            type=type,
        )
        self.attrname = attrname


class XmlModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            field_def = self.__class__.__dict__.get(k, None)
            if field_def:
                setattr(self, k, v)
            else:
                raise RuntimeError(
                    'Unexpected keyword argument "%s"' % k
                )

    @classmethod
    def load(cls, element):
        attribute_fields = {}
        tag_fields = {}
        for field_name, field in cls.__dict__.items():
            if isinstance(field, Attribute):
                attribute_fields[field_name] = field
            if isinstance(field, ChildTag):
                tag_fields[field_name] = field

        kwargs = {}
        for field_name, field in attribute_fields.items():
            attr_name = field_name
            if field.name is not None:
                attr_name = field.name
            value = element.attrib.get(attr_name, field.default)
            kwargs[field_name] = value

        tag_name_to_field_name = {}
        child_handlers = {}

        def create_child_handler(field):
            def child_handler(child):
                if field.attrname:
                    value = child.attrib.get(field.attrname, field.default)
                else:
                    value = child

                if field.type and issubclass(field.type, XmlModel):
                    return field.type.load(value)
                elif callable(field.type):
                    return field.type(value)
                else:
                    return value
            return child_handler

        for field_name, field in tag_fields.items():
            tag_name = field_name
            if field.name is not None:
                tag_name = field.name

            tag_name_to_field_name[tag_name] = field_name
            child_handlers[tag_name] = create_child_handler(field)

        for child in element:
            field_name = tag_name_to_field_name.get(child.tag, None)
            if field_name:
                handler = child_handlers.get(child.tag, None)
                if callable(handler):
                    kwargs[field_name] = handler(child)

        return cls(**kwargs)


class RunProperties(XmlModel):
    bold = ChildTag(type=OnOff, name='b', attrname='val')


class Style(XmlModel):
    style_type = Attribute(name='type', default='paragraph')
    style_id = Attribute(name='styleId', default='')
    name = ChildTag(attrname='val')
    run_properties = ChildTag(type=RunProperties, name='rPr')


class Styles(object):
    def __init__(self, styles):
        self.styles = styles
        styles_by_type = defaultdict(dict)
        for style in self.styles:
            styles_by_type[style.style_type][style.style_id] = style
        self.styles_by_type = dict(styles_by_type)

    @staticmethod
    def load(root):
        styles = [
            Style.load(element=element)
            for element in root
            if element.tag == 'style'
        ]
        return Styles(styles)

    def get_styles_by_type(self, style_type):
        return self.styles_by_type.get(style_type, {})
