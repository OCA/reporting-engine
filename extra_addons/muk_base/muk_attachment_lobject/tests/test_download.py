###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Large Objects Attachment 
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

import os
import time
import hmac
import base64
import hashlib
import logging

from odoo.http import request

from odoo.addons.muk_utils.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DownloadTestCase(common.HttpCase):
    
    def setUp(self):
        super(DownloadTestCase, self).setUp()
        self.attachment = self.env['ir.attachment'].sudo()
        self.params = self.env['ir.config_parameter'].sudo()
        self.location = self.params.get_param('ir_attachment.location')
        self.params.set_param('ir_attachment.location', 'lobject')

    def tearDown(self):
        self.params.set_param('ir_attachment.location', self.location)
        super(DownloadTestCase, self).tearDown()
    
    def test_attachment_download(self):
        self.authenticate('admin', 'admin')
        attach_01 = self.attachment.create({
            'name': "Test_01",
            'datas': base64.b64encode(b"\xff data")
        })
        attach_02 = self.attachment.create({
            'name': "Test_02",
        })
        self.assertTrue(attach_01.datas)
        self.assertFalse(attach_02.datas)
        data = {
            'model': 'ir.attachment',
            'field': 'store_lobject',
            'filename_field': 'datas_fname',
        }
        data.update({
            'id': attach_01.id,
        })
        self.assertTrue(self.url_open('/web/lobject', data=data, csrf=True))
        data.update({
            'id': attach_02.id,
        })
        self.assertTrue(self.url_open('/web/lobject', data=data, csrf=True))
        
        
    
   
      