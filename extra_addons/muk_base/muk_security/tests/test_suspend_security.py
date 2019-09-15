###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Security 
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

class SuspendSecurityTestCase(common.TransactionCase):
    
    def setUp(self):
        super(SuspendSecurityTestCase, self).setUp()
        
    def tearDown(self):
        super(SuspendSecurityTestCase, self).tearDown()
    
    def test_suspend_security(self):
        user_id = self.env.ref('base.user_demo').id
        tester = self.env.ref('base.user_root').sudo(user_id)
        with self.assertRaises(exceptions.AccessError):
            tester.write({'login': 'test'})
        tester.suspend_security().write({'login': 'test'})
        self.assertEqual(tester.login, 'test')
        self.assertEqual(tester.write_uid.id, user_id)
        
    def test_normalize(self):
        self.env['res.users'].browse(self.env['res.users'].suspend_security().env.uid)
    
    def test_search_one2many(self):
        user = self.env.ref('base.user_demo')
        model = self.env['res.partner'].sudo(user.id)
        self.assertTrue(model.env.user.id == user.id)
        normal_domain = [('user_ids.id', '=', model.env.uid)]
        suspend_domain = [('user_ids.id', '=', model.suspend_security().env.uid)]
        normal_partner = model.search(normal_domain, limit=1)
        suspend_partner = model.search(suspend_domain, limit=1)
        self.assertEqual(normal_partner, suspend_partner)
        normal_domain = [('user_ids', '=', model.env.uid)]
        suspend_domain = [('user_ids', '=', model.suspend_security().env.uid)]
        normal_partner = model.search(normal_domain, limit=1)
        suspend_partner = model.search(suspend_domain, limit=1)
        self.assertEqual(normal_partner, suspend_partner)
        normal_domain = [('user_ids.id', 'in', [model.env.uid])]
        suspend_domain = [('user_ids.id', 'in', [model.suspend_security().env.uid])]
        normal_partner = model.search(normal_domain, limit=1)
        suspend_partner = model.search(suspend_domain, limit=1)
        self.assertEqual(normal_partner, suspend_partner)
                