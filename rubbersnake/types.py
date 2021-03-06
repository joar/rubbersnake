# -*- coding:utf-8 -*-
#
#   Copyright 2013 Adam Höse <adis AT blad DOT is>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import sys
import datetime

class _BaseType(object):
    '''
    Common type properties and validations
    '''

    def __init__(self, default=None, max=None, min=None, null=False, mapping={}):
        #Parent class is specified in each type class, not here
        self.default = default
        self.max = max
        self.min = min
        self.null = null

        self.mapping = mapping

    def map(self):
        mapping = self.mapping.copy()
        if self.eltype is not None and "type" not in mapping:
            mapping["type"] = self.eltype
        return mapping if mapping else None

    def validate(self, value, name=''):

        #Validations that should be done for all types
        if self.null and value is None:
            return #No need to go any further

        #Validate against parent types
        if True not in [isinstance(value, i) for i in self.parent]:
            raise ValueError("'{0}' invalid for field '{1}'".format(value, name))

class String(_BaseType):
    '''
    String type
    '''

    def __init__(self, **kwargs):

        self.parent = [str]
        self.eltype = "string"

        #Unicode is deprecated in Py3K
        if sys.version_info[0] < 3:
            self.parent.append(unicode)
            
        super(String, self).__init__(**kwargs)

    def validate(self, value, name=''):
        super(String, self).validate(value, name=name)

        if value:
            if self.max and len(value) > self.max:
                raise OverflowError(
                    "'{0}' invalid '{1}'".format(value, name)
                )
            if self.min and len(value) < self.min:
                raise OverflowError(
                    "'{0}' invalid for field '{1}'".format(value, name)
                )

class Bool(_BaseType):
    '''
    Boolean type
    '''

    parent = [bool]
    eltype = "boolean"

class Num(_BaseType):
    '''
    Numeric type
    '''

    parent = [int, float]
    eltype = "integer"

    def validate(self, value, name=''):
        super(Num, self).validate(value, name=name)

        if value:
            if self.max and value > self.max:
                raise OverflowError(
                    "'{0}' invalid for field '{1}'".format(value, name)
                )
            if self.min and value < self.min:
                raise OverflowError(
                    "'{0}' invalid for field '{1}'".format(value, name)
                )

class DateTime(_BaseType):
    '''
    DateTime type
    '''

    parent = [datetime.datetime]
    eltype = "date"

    def validate(self, value, name=''):
        super(DateTime, self).validate(value, name=name)

        if value:
            if self.max and value > self.max:
                raise OverflowError(
                    "'{0}' invalid for field '{1}'".format(value, name)
                )
            if self.min and value < self.min:
                raise OverflowError(
                    "'{0}' invalid for field '{1}'".format(value, name)
                )

class Enum(_BaseType):
    '''
    Enum type
    '''

    def __init__(self, *values, **kwargs):
        self._values = values
        self.eltype = None
        super(Enum, self).__init__(**kwargs)

    def validate(self, value, name=''):
        if value not in self._values:
            raise ValueError("'{0}' invalid for field '{1}'".format(value, name))

class List(_BaseType):
    '''
    List type
    '''

    def __init__(self, parent, **kwargs):
        self.parent = parent
        if "default" not in kwargs:
            kwargs["default"] = []
        super(List, self).__init__(**kwargs)

    def map(self):
        return self.parent.map()

    def validate(self, value, name=''):
        #No need to run validation if null is allowed and value is null
        if self.null and value == None:
            return

        if not isinstance(value, tuple) and not isinstance(value, list):
            raise TypeError("List must contain iterable type for field '{0}'".format(name))

        for i in value:
            self.parent.validate(i, name=name)

class Dict(_BaseType):
    '''
    Dict type
    '''

    parent = [dict]

    def __init__(self, comp=None, **kwargs):
        comp = comp if comp is not None else {}
        self._comp = comp

        if kwargs.get("null"):
            default = None
        else:
            default = {}
            for key in self._comp:
                if isinstance(comp[key], _BaseType):
                    value = comp[key].default
                    if hasattr(value, "__call__"):
                        value = value()
                    default[key] = value

        kwargs["default"] = default
        super(Dict, self).__init__(**kwargs)

    def map(self):

        mapping = self.mapping.copy()
        if "type" not in mapping:
            mapping["type"] = "object"

        # Special objects (such as completions) will not properties
        if self._comp:
            properties = {}
            for key in self._comp:
                current = {}
                if current is not None:
                    properties[key] = self._comp[key].map()
            mapping["properties"] = properties

        return mapping

    def validate(self, value, name=''):
        #No need to run validation if null is allowed and value is null
        if self.null and value == None:
            return

        if value is None:
            raise ValueError("'{0}' invalid for field '{1}'".format(value, name))

        for key in self._comp.keys():
            self._comp[key].validate(
                value.get(key), 
                ".".join((name, key))
            )
