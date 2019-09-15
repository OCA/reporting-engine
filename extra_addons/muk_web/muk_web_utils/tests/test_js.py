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

import os
import json
import logging
import requests
import unittest

from odoo import _, http, tools, SUPERUSER_ID
from odoo.tests.common import HttpCase

from odoo.addons.muk_utils.tools.json import RecordEncoder 

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class WebSuite(HttpCase):
    
    @unittest.skip("")
    def test_js(self):
        self.browser_js('/web/tests?module=muk_web_utils&failfast', "", "", login='admin', timeout=1800)