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

class SearchParentTestCase(common.TransactionCase):
    
    def setUp(self):
        super(SearchParentTestCase, self).setUp()
        self.model = self.env['res.partner.category']
        
    def tearDown(self):
        super(SearchParentTestCase, self).tearDown()
    
    def _evaluate_parent_result(self, parents, records):
        for parent in parents:
            self.assertTrue(
                not parent.parent_id or 
                parent.parent_id.id not in records.ids
            )
    
    def test_search_parents(self):
        records = self.model.search([])
        parents = self.model.search_parents([])
        self._evaluate_parent_result(parents, records)
    
    def test_search_parents_domain(self):
        records = self.model.search([('id', '!=', 1)])
        parents = self.model.search_parents([('id', '!=', 1)])
        self._evaluate_parent_result(parents, records)
    
    def test_search_read_parents(self):
        parents = self.model.search_parents([])
        read_names = parents.read(['name'])
        search_names = self.model.search_read_parents([], ['name'])
        self.assertTrue(read_names == search_names)
        
        