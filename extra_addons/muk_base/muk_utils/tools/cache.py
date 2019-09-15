###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Utils 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import time
import logging
import datetime
import functools

_logger = logging.getLogger(__name__)


#----------------------------------------------------------
# Properties
#----------------------------------------------------------

class cached_property(object):

    def __init__(self, timeout=None):
        self.timeout = timeout

    def __call__(self, func):
        return functools.update_wrapper(self, func)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        try:
            value, last_updated =  obj.__dict__[self.__name__]
        except KeyError:
            pass
        else:
            if self.timeout is None:
                return value
            elif self.timeout >= time.time() - last_updated:
                return value
        value = self.__wrapped__(obj)
        obj.__dict__[self.__name__] = (value, time.time())
        return value

    def __delete__(self, obj):
        obj.__dict__.pop(self.__name__, None)

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = (value, time())