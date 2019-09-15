###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK DB Filter 
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

import random
import re
import logging

from odoo import http, tools
from odoo.http import request

from odoo.addons.muk_utils.tools.patch import monkey_patch

_logger = logging.getLogger(__name__)

@monkey_patch(http)
def db_filter(dbs, httprequest=None):
    httprequest = httprequest or request.httprequest
    dbs = db_filter.super(dbs, httprequest=httprequest)
    filter = httprequest.environ.get('HTTP_X_ODOO_DBFILTER')
    return [db for db in dbs if re.match(filter, db)] if filter else dbs