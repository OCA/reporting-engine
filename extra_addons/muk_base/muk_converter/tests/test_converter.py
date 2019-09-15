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

import os
import base64
import logging
import unittest

from odoo.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class ConverterTestCase(common.TransactionCase):
    
    def setUp(self):
        super(ConverterTestCase, self).setUp()
        self.params = self.env['ir.config_parameter']
        self.store = self.env['muk_converter.store'].sudo()
        self.converter = self.env['muk_converter.converter']
        self.store_count = self.store.search([], count=True)
        self.params.set_param('muk_converter.service', 'unoconv')

    def tearDown(self):
        super(ConverterTestCase, self).tearDown()
        
    def test_formats(self):
        self.assertTrue(self.converter.formats())
    
    def test_imports(self):
        self.assertTrue(self.converter.imports())
    
    @unittest.skipIf(os.environ.get('TRAVIS', False), "Skipped for Travis CI")
    def test_convert_basic(self):
        with open(os.path.join(_path, 'tests/data', 'sample.png'), 'rb') as file:
            self.assertTrue(self.converter.convert('sample.png', base64.b64encode(file.read())))
            
    @unittest.skipIf(os.environ.get('TRAVIS', False), "Skipped for Travis CI")
    def test_convert_format(self):
        with open(os.path.join(_path, 'tests/data', 'sample.png'), 'rb') as file:
            self.assertTrue(self.converter.convert('sample.png', base64.b64encode(file.read()), format="html"))
    
    @unittest.skipIf(os.environ.get('TRAVIS', False), "Skipped for Travis CI")
    def test_convert_stored(self):
        with open(os.path.join(_path, 'tests/data', 'sample.png'), 'rb') as file:
            self.assertTrue(self.converter.convert('sample.png', base64.b64encode(file.read())))
            self.assertTrue(self.store.search([], count=True) >= self.store_count)
            self.assertTrue(self.converter.convert('sample.png', base64.b64encode(file.read())))
    
    @unittest.skipIf(os.environ.get('TRAVIS', False), "Skipped for Travis CI")
    def test_convert_recompute(self):
        with open(os.path.join(_path, 'tests/data', 'sample.png'), 'rb') as file:
            self.assertTrue(self.converter.convert('sample.png', base64.b64encode(file.read()), recompute=True, store=False))
            self.assertTrue(self.store.search([], count=True) == self.store_count)
            self.assertTrue(self.converter.convert('sample.png', base64.b64encode(file.read())))