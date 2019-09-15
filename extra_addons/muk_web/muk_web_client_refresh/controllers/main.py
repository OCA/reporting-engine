###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Refresh 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class RefreshController(http.Controller):

    @http.route('/config/muk_web_client_refresh.refresh_delay', type='json', auth="user")
    def refresh_delay(self, **kw):
        params = request.env['ir.config_parameter'].sudo()
        return {
            'refresh_delay': int(params.get_param("muk_web_client_refresh.refresh_delay", default=1000))
        }