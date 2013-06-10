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
from .exceptions import *

class _BaseType(object):
    '''
    Common type properties and validations
    '''

    def __init__(self, default=None, max=None, min=None, null=False):
        #Parent class is specified in each type class, not here
        self.default = default() if hasattr(default, '__call__') else default
        self.max = max
        self.min = min
        self.null = null

    def validate(self, value):

        #Validations that should be done for all types
        if not self.null and value == None:
            raise ValueNullException()

        #Validate against parent types
        if True not in [isinstance(value, i) for i in self.parent]:
            if not (self.null and isinstance(value, _BaseType)):
                raise ValueError("Value '{0}' not allowed".format(value))

class String(_BaseType):
    '''
    String type
    '''

    def __init__(self, **kwargs):

        self.parent = [str]

        #Unicode is deprecated in Py3K
        if sys.version_info[0] < 3:
            self.parent.append(unicode)
            
        super(String, self).__init__(**kwargs)

    def validate(self, value):
        super(String, self).validate(value)

        if value:
            if self.max and len(value) > self.max:
                raise ValueTooLargeException()
            if self.min and len(value) < self.min:
                raise ValueTooSmallException()

class Bool(_BaseType):
    '''
    Boolean type
    '''

    parent = [bool]

class Num(_BaseType):
    '''
    Numeric type
    '''

    parent = [int, float]

    def validate(self, value):
        super(Num, self).validate(value)

        if value:
            if self.max and value > self.max:
                raise ValueTooLargeException()
            if self.min and value < self.min:
                raise ValueTooSmallException()

class DateTime(_BaseType):
    '''
    DateTime type
    '''

    parent = [datetime.datetime]

    def validate(self, value):
        super(DateTime, self).validate(value)

        if value:
            if self.max and value > self.max:
                raise ValueTooLargeException()
            if self.min and value < self.min:
                raise ValueTooSmallException()

class Enum(_BaseType):
    '''
    Enum type
    '''

    def __init__(self, *values, **kwargs):
        self._values = values
        super(Enum, self).__init__(**kwargs)

    def validate(self, value):
        if value not in self._values:
            raise ValueException("Value {0} not valid for this enum".format(value))

class List(_BaseType):
    '''
    List type
    '''

    def __init__(self, *args, **kwargs):
        self.parent = args
        super(List, self).__init__(**kwargs)

    def validate(self, value):
        #No need to run validation if null is allowed and value is null
        if self.null and value == None:
            return

        if not isinstance(value, tuple) and not isinstance(value, list):
            raise ValueException("List neither tuple nor list")

        for i in value:
            valid = False
            for p in self.parent:
                try:
                    p.validate(i)
                    valid = True
                except Exception as e:
                    pass
            if not valid:
                raise ValueError("Value '{0}' not allowed".format(i))

class Dict(_BaseType):
    '''
    Dict type
    '''

    parent = [dict]

    def __init__(self, comp={}, **kwargs):
        self._comp = comp
        super(Dict, self).__init__(**kwargs)

    def validate(self, value):
        #No need to run validation if null is allowed and value is null
        if self.null and value == None:
            return

        if value == None:
            raise ValueNullException()

        if True not in [isinstance(value, i) for i in self.parent]:
            raise ValueException("Value invalid")

        for key in self._comp.keys():
            self._comp[key].validate(value.get(key))
