###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Converter 
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

import base64
import hashlib
import logging

from odoo import api, models, fields, SUPERUSER_ID

from odoo.addons.muk_converter.service.unoconv import unoconv
from odoo.addons.muk_converter.service.provider import provider

_logger = logging.getLogger(__name__)

class Converter(models.AbstractModel):
    
    _name = 'muk_converter.converter'
    _description = 'Converter'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.model
    def formats(self):
        return self._provider().formats

    @api.model
    def imports(self):
        return self._provider().imports
    
    @api.model
    def convert(self, filename, content, format="pdf", recompute=False, store=True):
        binary_content = base64.b64decode(content)
        checksum = hashlib.sha1(binary_content).hexdigest()
        stored = self._retrieve(checksum, format)
        if not recompute and stored.exists():
            return base64.b64encode(stored.content)
        else:
            name = "%s.%s" % (filename, format)
            output = self._parse(filename, binary_content, format)
            if store:
                self._store(checksum, name, output, format, stored)
            return base64.b64encode(output)
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _provider(self):
        params = self.env['ir.config_parameter'].sudo()
        service = params.get_param('muk_converter.service')
        if service == 'unoconv':
            return unoconv
        else:
            provider.env = self.env
            return provider

    @api.model
    def _parse(self, filename, content, format):
        return self._provider().convert(content, filename=filename, format=format)
    
    @api.model
    def _retrieve(self, checksum, format):
        domain = [["checksum", "=", checksum], ["format", "=", format]]
        return self.env['muk_converter.store'].sudo().search(domain, limit=1)
    
    @api.model
    def _store(self, checksum, filename, content, format, stored):
        if stored and stored.exists():
            stored.write({'used_date': fields.Datetime.now})
        else: 
            self.env['muk_converter.store'].sudo().create({
                'checksum': checksum,
                'format': format,
                'content_fname': filename,
                'content': content})