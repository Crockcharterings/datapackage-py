from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import copy
import json
import jsonschema
from .exceptions import (
    SchemaError, ValidationError
)


class Schema(object):
    def __init__(self, schema):
        self._schema = self._load_schema(schema)
        validator_class = jsonschema.validators.validator_for(self._schema)
        self._validator = validator_class(self._schema)
        self._check_schema()

    def to_dict(self):
        return copy.deepcopy(self._schema)

    def validate(self, data):
        try:
            self._validator.validate(data)
        except jsonschema.exceptions.ValidationError as e:
            six.raise_from(ValidationError.create_from(e), e)

    def _load_schema(self, schema):
        the_schema = schema

        if isinstance(schema, six.string_types):
            try:
                the_schema = json.load(open(schema, 'r'))
            except IOError as e:
                msg = 'Unable to load JSON at "{0}"'
                six.raise_from(SchemaError(msg.format(schema)), e)
        elif isinstance(the_schema, dict):
            the_schema = copy.deepcopy(the_schema)
        else:
            msg = 'Schema must be a "dict", but was a "{0}"'
            raise SchemaError(msg.format(type(the_schema).__name__))

        return the_schema

    def _check_schema(self):
        try:
            self._validator.check_schema(self._schema)
        except jsonschema.exceptions.SchemaError as e:
            six.raise_from(SchemaError.create_from(e), e)

    def __getattr__(self, name):
        if name in self.__dict__.get('_schema', {}):
            return copy.deepcopy(self._schema[name])

        msg = '\'{0}\' object has no attribute \'{1}\''
        raise AttributeError(msg.format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self.__dict__.get('_schema', {}):
            raise AttributeError('can\'t set attribute')
        super(self.__class__, self).__setattr__(name, value)

    def __dir__(self):
        return list(self.__dict__.keys()) + list(self._schema.keys())
