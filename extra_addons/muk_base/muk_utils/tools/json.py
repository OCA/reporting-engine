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

import json
import logging
import datetime

from odoo import models, tools

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# JSON Encoder
#----------------------------------------------------------

class ResponseEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        if isinstance(obj, datetime.date):
            return obj.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode()
        return json.JSONEncoder.default(self, obj)

class RecordEncoder(ResponseEncoder):
    
    def default(self, obj):
        if isinstance(obj, models.BaseModel):
            return obj.name_get()
        return ResponseEncoder.default(self, obj)
        