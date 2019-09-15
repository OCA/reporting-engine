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

from odoo import api, models, fields

from odoo.addons.muk_security.tools.security import NoSecurityUid

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    
    _inherit = 'base'

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------

    def _filter_access_rules(self, operation):
        if isinstance(self.env.uid, NoSecurityUid):
            return self
        return super(Base, self)._filter_access_rules(operation)
    
    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        if isinstance(self.env.uid, NoSecurityUid):
            return None
        return super(Base, self)._apply_ir_rules(query, mode=mode)
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------

    @api.model
    def suspend_security(self, user=None):
        return self.sudo(user=NoSecurityUid(user or self.env.uid))
    
    @api.multi
    def check_access_rule(self, operation):
        if isinstance(self.env.uid, NoSecurityUid):
            return None
        return super(Base, self).check_access_rule(operation)
    
    @api.model
    def check_field_access_rights(self, operation, fields):    
        if isinstance(self.env.uid, NoSecurityUid):
            return fields or list(self._fields)
        return super(Base, self).check_field_access_rights(operation, fields)