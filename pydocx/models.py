# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict


class XmlField(object):
    '''
    Represents a generic XML field which can be an attribute or tag.
    '''
    def __init__(self, name=None, default=None, type=None):
        self.name = name
        self.default = default
        self.type = type


class XmlAttribute(XmlField):
    '''
    Represents that the field to be processed is an attribute
    '''
    pass


class XmlChild(XmlField):
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
        super(XmlChild, self).__init__(
            name=name,
            default=default,
            type=type,
        )
        self.attrname = attrname


class XmlCollection(XmlField):
    '''
    Represents a collection of elements. To define a field of this type,
    a mapping dictionary must be passed in specifying the name of the child
    elements and a callable handler for each.

    Example:

    class ParkingLot(XmlModel):
        cars = Collection({
            'car': Car,
            'truck': Truck,
        })

    In the above example, 'car' and 'truck' are element names. 'Car' and
    'Truck' are (callable) handlers for those elements. The handler may
    optionally be a XmlModel.
    An instance of ParkingLot will have an attribute 'cars' that is a list.
    '''

    def __init__(self, name_to_type_map, default=None):
        if default is None:
            default = []
        super(XmlCollection, self).__init__(self, default=default)
        self.name_to_type_map = name_to_type_map

    def get_handler_for_tag(self, tag):
        return self.name_to_type_map.get(tag)


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

    def __repr__(self):
        return '{klass}({kwargs})'.format(
            klass=self.__class__.__name__,
            kwargs=', '.join('{field}={value}'.format(
                field=field,
                value=repr(value),
            ) for field, value in self.items()),
        )

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
        collections = {}
        # Enumerate the defined fields and separate them into attributes and
        # tags
        for field_name, field in cls.__dict__.items():
            if isinstance(field, XmlAttribute):
                attribute_fields[field_name] = field
            if isinstance(field, XmlChild):
                tag_fields[field_name] = field
            if isinstance(field, XmlCollection):
                collections[field_name] = field

        kwargs = {}

        for field_name in collections.keys():
            kwargs[field_name] = []

        # Evaluate each of the attribute fields against the given element
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

        # Build a mapping of tag names to collections
        collection_member_to_collections = defaultdict(list)
        for field_name, field in collections.items():
            for tag_name in field.name_to_type_map.keys():
                collection_member_to_collections[tag_name].append(field_name)

        if element:
            # Process each child
            for child in element:
                tag = child.tag
                # Does this child have a corresponding field?
                field_name = tag_name_to_field_name.get(tag, None)
                if field_name:
                    # Execute the handler
                    handler = child_handlers.get(tag, None)
                    if callable(handler):
                        kwargs[field_name] = handler(child)

                # Does a this child belong to a collection?
                parent_collections = collection_member_to_collections.get(
                    tag,
                    [],
                )
                for field_name in parent_collections:
                    collection = collections.get(field_name)
                    if collection:
                        # different collection definitions may define different
                        # handlers for the same child
                        handler = collection.get_handler_for_tag(tag)
                        # If the handler is a XmlModel we want to use the load
                        # method, not the constructor
                        if issubclass(handler, XmlModel):
                            handler = handler.load
                        if callable(handler):
                            item = handler(child)
                            kwargs[field_name].append(item)

        # Create a new instance using the values we've calculated
        return cls(**kwargs)
