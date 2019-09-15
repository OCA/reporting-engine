###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Utils 
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
import base64
import logging

from odoo import http
from odoo.http import request
from odoo.tools.misc import str2bool

_logger = logging.getLogger(__name__)

class AttachmentController(http.Controller):
    
    @http.route('/utils/attachment/add', type='http', auth="user", methods=['POST'])
    def add_attachment(self, ufile, temporary=False, **kw):
        tmp = temporary and str2bool(temporary) or False
        name = "Access Attachment: %s" % ufile.filename
        attachment = request.env['ir.attachment'].create({
            'name': tmp and "%s (Temporary)" % name or name,
            'datas': base64.b64encode(ufile.read()),
            'datas_fname': ufile.filename,
            'type': 'binary',
            'public': False,
            'temporary': tmp,
        })
        attachment.generate_access_token()
        if ufile.mimetype and ufile.mimetype != 'application/octet-stream': 
            attachment.sudo().write({
                'mimetype': ufile.mimetype,
            })
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        result = attachment.read(['name', 'datas_fname', 'mimetype', 'checksum', 'access_token'])[0]
        result['url'] = '%s/web/content/%s?access_token=%s' % (base_url, attachment.id, attachment.access_token)
        return json.dumps(result)
        