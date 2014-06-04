from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


class XmlField(object):
    '''
    Represents a generic XML field which can be an attribute or tag.
    '''
    def __init__(self, name=None, default=None, type=None):
        self.name = name
        self.default = default
        self.type = type


class Attribute(XmlField):
    '''
    Represents that the field to be processed is an attribute
    '''
    pass


class ChildTag(XmlField):
    '''
    Represents that the field to be processed is a child
    '''
    def __init__(self, name=None, default=None, type=None, attrname=None):
        '''
        If specified, `name` indicates the XML tag name.
        If specified, `default` indicates the value of the field if the tag
        isn't present.
        If specified, the raw XML value will be passed to `type`.
        If specified, `attrname` indicates that the value is stored in an
        attribute on the child.
        '''
        super(ChildTag, self).__init__(
            name=name,
            default=default,
            type=type,
        )
        self.attrname = attrname


class XmlModel(object):
    '''
    Xml models are defined by inheriting this class, and then specifying class
    variables to define the structure of the XML data.

    Example:

    class Person(XmlModel):
        first_name = Attribute(name='first', default='')
        age = Attribute(default='')
        address = ChildTag(attrname='val')

    xml = """<?xml version="1.0"?>
    <person first='Dave' age='25'>
        <address val="123 Shadywood"/>
    </person>
    """

    person = Person.load(xml)
    '''

    def __init__(self, **kwargs):
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, XmlField):
                value = kwargs.get(field_name, field.default)
                setattr(self, field_name, value)

    def items(self):
        '''
        A generator that loops through each of the defined fields for the
        model, and yields back only those fields which have been set to a value
        that isn't the field's default.
        '''
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, XmlField):
                value = getattr(self, field_name, field.default)
                if value != field.default:
                    yield field_name, value

    @classmethod
    def load(cls, element):
        attribute_fields = {}
        tag_fields = {}
        # Enumerate the defined fields and separate them into attributes and
        # tags
        for field_name, field in cls.__dict__.items():
            if isinstance(field, Attribute):
                attribute_fields[field_name] = field
            if isinstance(field, ChildTag):
                tag_fields[field_name] = field

        # Evaluate each of the attribute fields against the given element
        kwargs = {}
        for field_name, field in attribute_fields.items():
            attr_name = field_name
            if field.name is not None:
                attr_name = field.name
            value = element.attrib.get(attr_name, field.default)
            kwargs[field_name] = value

        # Child tag fields may specify a handler/type, which is responsible for
        # parsing the child tag
        tag_name_to_field_name = {}
        child_handlers = {}

        def create_child_handler(field):
            def child_handler(child):
                # If attrname is set, then the value is an attribute on the
                # child
                if field.attrname:
                    value = child.attrib.get(field.attrname, field.default)
                else:
                    # Otherwise it's just the child
                    value = child

                # The type may be an XmlModel, if so, construct a new instance
                # using XmlModel.load
                if field.type and issubclass(field.type, XmlModel):
                    return field.type.load(value)
                # Or it could just be something that we can call
                elif callable(field.type):
                    return field.type(value)
                else:
                    return value
            return child_handler

        # Evaluate the child tags
        for field_name, field in tag_fields.items():
            # By default, the name is whatever the field name is, unless the
            # tag definition specifies an override name
            tag_name = field_name
            if field.name is not None:
                tag_name = field.name

            # Based on the tag name, we need to know what the field name is
            tag_name_to_field_name[tag_name] = field_name
            # Save the handler
            child_handlers[tag_name] = create_child_handler(field)

        # Process each child
        for child in element:
            # Does this child have a corresponding field?
            field_name = tag_name_to_field_name.get(child.tag, None)
            if field_name:
                # Execute the handler
                handler = child_handlers.get(child.tag, None)
                if callable(handler):
                    kwargs[field_name] = handler(child)
        # Create a new instance using the values we've calculated
        return cls(**kwargs)
