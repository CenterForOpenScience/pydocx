from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


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
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, XmlField):
                value = kwargs.get(field_name, field.default)
                setattr(self, field_name, value)

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
