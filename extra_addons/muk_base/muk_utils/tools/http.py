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

import urllib
import base64
import logging

from werkzeug.datastructures import CombinedMultiDict

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Header Helper
#----------------------------------------------------------

def decode_http_basic_authentication_value(value):
    try:
        username, password = base64.b64decode(value).decode().split(':', 1)
        return urllib.parse.unquote(username), urllib.parse.unquote(password)
    except:
        return None, None

def decode_http_basic_authentication(encoded_header):
    header_values = encoded_header.strip().split(' ')
    if len(header_values) == 1:
        return decode_http_basic_authentication_value(header_values[0])
    if len(header_values) == 2 and header_values[0].strip().lower() == 'basic':
        return decode_http_basic_authentication_value(header_values[1])
    return None, None

#----------------------------------------------------------
# Werkzeug Helper
#----------------------------------------------------------

def request_params(httprequest):
    return CombinedMultiDict([
        httprequest.args,
        httprequest.form,
        httprequest.files
    ])