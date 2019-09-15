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
import logging

from odoo.addons.iap import jsonrpc

from odoo.addons.muk_utils.tools.cache import cached_property
from odoo.addons.muk_utils.tools.file import guess_extension

_logger = logging.getLogger(__name__)

CONVERTER_DEFAULT_ENDPOINT = 'https://iap-converter.mukit.at'
CONVERTER_ENDPOINT_FORMATS = '/iap/converter/1/formats'
CONVERTER_ENDPOINT_IMPORTS = '/iap/converter/1/imports'
CONVERTER_ENDPOINT_CONVERT = '/iap/converter/1/convert'

class RemoteConverter(object):
        
    @property
    def env(self):
        return self._params

    @env.setter
    def env(self, env):
        self._params = env['ir.config_parameter'].sudo()
        self._account = env['iap.account'].get('muk_converter')
    
    @property
    def params(self):
        return self._params
    
    @property
    def account(self):
        return self._account
    
    @cached_property(timeout=3600)
    def formats(self):
        print("FORMATS")
        return jsonrpc(self.endpoint(CONVERTER_ENDPOINT_FORMATS), params=self.payload())
    
    @cached_property(timeout=3600)
    def imports(self):
        return jsonrpc(self.endpoint(CONVERTER_ENDPOINT_IMPORTS), params=self.payload())
    
    def endpoint(self, route):
        return "%s%s" % (self.params.get_param('muk_converter.endpoint', CONVERTER_DEFAULT_ENDPOINT), route)

    def payload(self, params={}):
        params.update({
            'account_token': self.account.account_token,
            'database_uuid': self.params.get_param('database.uuid'),
        })
        return params
    
    def convert(self, binary, mimetype=None, filename=None, export="binary", doctype="document", format="pdf"):
        """ Converts a binary value to the given format.
        
            :param binary: The binary value.
            :param mimetype: The mimetype of the binary value.
            :param filename: The filename of the binary value.
            :param export: The output format (binary, file, base64).
            :param doctype: Specify the document type (document, graphics, presentation, spreadsheet).
            :param format: Specify the output format for the document.
            :return: Returns the output depending on the given format.
            :raises ValueError: The file extension could not be determined or the format is invalid.
        """
        params = {
            'format': format,
            'doctype': doctype,
            'mimetype': mimetype,
            'filename': filename,
            'content': base64.b64encode(binary),
        }
        result = jsonrpc(self.endpoint(CONVERTER_ENDPOINT_CONVERT), params=self.payload(params))
        if export == 'base64':
            return result
        if export == 'file':
            output = io.BytesIO()
            output.write(base64.b64decode(result))
            output.close()
            return output
        else:
            return base64.b64decode(result)
        
provider = RemoteConverter()