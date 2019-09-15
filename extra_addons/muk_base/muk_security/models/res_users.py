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

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

from odoo.addons.muk_security.tools.security import NoSecurityUid
from odoo.addons.muk_security.tools.security import convert_security_uid


_logger = logging.getLogger(__name__)

class AccessUser(models.Model):
    
    _inherit = 'res.users'

    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def browse(self, arg=None, *args, **kwargs):
        return super(AccessUser, self).browse(convert_security_uid(arg), *args, **kwargs)
    
    @classmethod
    def _browse(cls, ids, *args, **kwargs):
        access_ids = [convert_security_uid(id) for id in ids]
        return super(AccessUser, cls)._browse(access_ids, *args, **kwargs)