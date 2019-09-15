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

class AccessGroupsTestCase(common.TransactionCase):
    
    def setUp(self):
        super(AccessGroupsTestCase, self).setUp()
        self.user_id = self.ref('base.user_demo')
        self.group_id = self.ref('base.group_system')
        self.groups = self.env['muk_security.access_groups']
        self.group01 = self.groups.create({
            'name': 'Group 01',
            'explicit_users': [(6, 0, [self.user_id])]})
        self.group02 = self.groups.create({
            'name': 'Group 02',
            'groups': [(6, 0, [self.group_id])]})
        self.user = self.env['res.users'].browse(self.user_id)
        self.group = self.env['res.groups'].browse(self.group_id)
        
    def tearDown(self):
        super(AccessGroupsTestCase, self).tearDown()
    
    def test_access_groups_users(self):
        count = len(self.group02.users)
        self.group02.write({'explicit_users': [(6, 0, [self.user_id])]})
        self.assertTrue(len(self.group02.users) > count)
        
    def test_access_groups_groups(self):
        count = len(self.group01.users)
        self.group01.write({'groups': [(6, 0, [self.group_id])]})
        self.assertTrue(len(self.group01.users) > count)
        
    def test_access_groups_groups_group(self):
        count = len(self.group02.users)
        self.group.write({'users': [(4, self.user_id)]})
        self.assertTrue(len(self.group02.users) > count)
        
    def test_access_groups_groups_user(self):
        count = len(self.group02.users)
        self.user.write({'groups_id':[(4, self.group_id)]})
        self.assertTrue(len(self.group02.users) > count)
        
    def test_access_groups_parent(self):
        count = len(self.group02.users)
        self.group02.write({'parent_group': self.group01.id})
        self.assertTrue(len(self.group02.users) > count)
    
    def test_access_groups_parent_multi(self):
        group01 = self.groups.create({'name': 'MGroup 01'})
        group02 = self.groups.create({'name': 'MGroup 02', 'parent_group': group01.id})
        group03 = self.groups.create({'name': 'MGroup 03', 'parent_group': group02.id})
        init_count = len(group03.users)
        group02.write({'explicit_users': [(6, 0, [self.user_id])]})
        self.assertTrue(len(group03.users) > init_count)
        updated_count = len(group03.users)
        group01.write({'groups': [(6, 0, [self.group_id])]})
        self.assertTrue(len(group03.users) > updated_count)