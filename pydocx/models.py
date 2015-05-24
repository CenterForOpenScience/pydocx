# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict


class XmlException(Exception):
    pass


class XmlRootElementMismatchException(XmlException):
    pass


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


class XmlContent(XmlField):
    pass


class XmlCollection(XmlField):
    '''
    Represents an ordered collection of elements.

    To define a field of this type, pass in a sequence of tuples that specify
    the tag name of the XML child, and the callable handler:

    class ParkingLot(XmlModel):
        cars = Collection(
            ('car', Car),
            ('truck', Truck),
        )

    Alternatively, the callable handlers define their own XML_TAG declaration.
    In this case, simply pass in the sequence of handlers:

    class Car(XmlModel):
        XML_TAG = 'car'

    class Truck(XmlModel):
        XML_TAG = 'truck'

    class ParkingLot(XmlModel):
        cars = Collection(
            Car,
            Truck,
        )

    In the above examples, 'car' and 'truck' are element names. 'Car' and
    'Truck' are (callable) handlers for those elements. The handler may
    optionally be a XmlModel.

    An instance of ParkingLot will have an attribute 'cars' that is a list.
    '''

    def __init__(self, *types, **kwargs):
        default = kwargs.pop('default', [])
        super(XmlCollection, self).__init__(self, default=default)
        name_to_type_map = {}
        for type_spec in types:
            if isinstance(type_spec, tuple):
                tag_name, model = type_spec
            else:
                model = type_spec
                tag_name = getattr(model, 'XML_TAG')
            name_to_type_map[tag_name] = model
        self.name_to_type_map = name_to_type_map

    def get_handler_for_tag(self, tag):
        return self.name_to_type_map.get(tag)


class XmlModel(object):
    '''
    Xml models are defined by inheriting this class, and then specifying class
    variables to define the structure of the XML data.

    Example:

    class Person(XmlModel):
        XML_TAG = 'person'

        first_name = XmlAttribute(name='first', default='')
        age = XmlAttribute(default='')
        address = XmlChild(attrname='val')

    xml = """<?xml version="1.0"?>
    <person first='Dave' age='25'>
        <address val="123 Shadywood"/>
    </person>
    """

    person = Person.load(xml)
    '''

    def __init__(
        self,
        parent=None,
        **kwargs
    ):
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, XmlField):
                value = kwargs.get(field_name, field.default)
                if hasattr(value, 'parent'):
                    value.parent = self
                if isinstance(field, XmlCollection):
                    for item in value:
                        if hasattr(item, 'parent'):
                            item.parent = self
                setattr(self, field_name, value)

        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def __repr__(self):
        return '{klass}({kwargs})'.format(
            klass=self.__class__.__name__,
            kwargs=', '.join('{field}={value}'.format(
                field=field,
                value=repr(value),
            ) for field, value in self.fields),
        )

    @property
    def fields(self):
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
        xml_tag_decl = getattr(cls, 'XML_TAG', None)
        if element is not None and xml_tag_decl:
            if xml_tag_decl != element.tag:
                raise XmlRootElementMismatchException(
                    'Expected root element {tag} but got {other} instead'.format(  # noqa
                        tag=xml_tag_decl,
                        other=element.tag,
                    ),
                )

        attribute_fields = {}
        tag_fields = {}
        collections = {}

        kwargs = {}

        # Enumerate the defined fields and separate them into attributes and
        # tags
        for field_name, field in cls.__dict__.items():
            if isinstance(field, XmlAttribute):
                attribute_fields[field_name] = field
            if isinstance(field, XmlChild):
                tag_fields[field_name] = field
            if isinstance(field, XmlContent):
                kwargs[field_name] = element.text
            if isinstance(field, XmlCollection):
                collections[field_name] = field

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
            # The attribute name is whatever the field name is, unless:
            # field.name is set, or
            # field.type.XML_TAG is set
            tag_name = field_name

            if field.name is not None:
                tag_name = field.name
            elif field.type:
                field_type_tag = getattr(field.type, 'XML_TAG', None)
                if field_type_tag:
                    tag_name = field_type_tag

            assert tag_name

            # Based on the tag name, we need to know what the field name is
            tag_name_to_field_name[tag_name] = field_name
            # Save the handler
            child_handlers[tag_name] = create_child_handler(field)

        # Build a mapping of tag names to collections
        collection_member_to_collections = defaultdict(list)
        for field_name, field in collections.items():
            for tag_name in field.name_to_type_map.keys():
                collection_member_to_collections[tag_name].append(field_name)

        if element is not None:
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
