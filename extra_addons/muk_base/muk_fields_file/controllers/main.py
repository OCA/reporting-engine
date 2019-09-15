###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Filestore Field 
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

import logging

from werkzeug import utils
from werkzeug import wrappers

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
    
def file_content(xmlid=None, model=None, id=None, field='content', unique=False,
                    filename=None, filename_field='content_fname', download=False, 
                    mimetype=None, default_mimetype='application/octet-stream', env=None):
    return request.registry['ir.http'].file_content(
        xmlid=xmlid, model=model, id=id, field=field, unique=unique, 
        filename=filename, filename_field=filename_field, download=download, 
        mimetype=mimetype, default_mimetype=default_mimetype, env=env)

class FileController(http.Controller):
    
    @http.route([
        '/web/file',
        '/web/file/<string:xmlid>',
        '/web/file/<string:xmlid>/<string:filename>',
        '/web/file/<int:id>',
        '/web/file/<int:id>/<string:filename>',
        '/web/file/<int:id>-<string:unique>',
        '/web/file/<int:id>-<string:unique>/<string:filename>',
        '/web/file/<string:model>/<int:id>/<string:field>',
        '/web/file/<string:model>/<int:id>/<string:field>/<string:filename>'
    ], type='http', auth="public")
    def content_file(self, xmlid=None, model=None, id=None, field='content',
                        filename=None, filename_field='content_fname', unique=None, 
                        mimetype=None, download=None, data=None, token=None):
        status, headers, content = file_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype)
        if status == 304:
            response = wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            headers.append(('Content-Length', content.seek(0, 2)))
            content.seek(0, 0)
            response =  wrappers.Response(content, headers=headers, status=status, direct_passthrough=True)
        if token:
            response.set_cookie('fileToken', token)
        return response