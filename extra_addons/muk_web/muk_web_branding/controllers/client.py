###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Branding 
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

import werkzeug

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import make_conditional, get_last_modified
from odoo.addons.web.controllers.main import manifest_glob, concat_xml
from odoo.addons.web.controllers.main import WebClient

class WebClient(WebClient):

    @http.route('/web/webclient/qweb', type='http', auth="none", cors="*")
    def qweb(self, mods=None, db=None):
        files = [f[0] for f in manifest_glob('qweb', addons=mods, db=db)]
        last_modified = get_last_modified(files)
        if request.httprequest.if_modified_since and request.httprequest.if_modified_since >= last_modified:
            return werkzeug.wrappers.Response(status=304)
        content, checksum = concat_xml(files)
        if request.context and request.context.get('lang') == 'en_US':
            if request.session.db and request.env:
                content =  request.env['muk_branding.debranding'].debrand(content)
        return make_conditional(
            request.make_response(content, [('Content-Type', 'text/xml')]), last_modified, checksum
        )

    @http.route('/web/webclient/translations', type='json', auth="none")
    def translations(self, mods=None, lang=None):
        res = super(WebClient, self).translations(mods, lang)
        for module_key, module_vals in res['modules'].items():
            for message in module_vals['messages']:
                message['id'] = request.env['muk_branding.debranding'].debrand(message['id'])
                message['string'] = request.env['muk_branding.debranding'].debrand(message['string'])
        return res
    
    
    