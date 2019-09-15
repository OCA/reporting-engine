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

import os
import base64
import logging

from odoo import exceptions
from odoo.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class MigrationTestCase(common.TransactionCase):
    
    def setUp(self):
        super(MigrationTestCase, self).setUp()
        self.model = self.env['ir.attachment']
        self.params = self.env['ir.config_parameter'].sudo()
        self.location = self.params.get_param('ir_attachment.location')
        if self.location == 'file':
            self.params.set_param('ir_attachment.location', 'db')
        else:
            self.params.set_param('ir_attachment.location', 'file')

    def tearDown(self):
        self.params.set_param('ir_attachment.location', self.location)
        super(MigrationTestCase, self).tearDown()
    
    def test_migration(self):
        self.model.search([], limit=25).migrate(batch_size=5)
    