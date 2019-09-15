###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Backend Theme 
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

from odoo import models, fields, api

class ResUsers(models.Model):
    
    _inherit = 'res.users'
    
    #----------------------------------------------------------
    # Defaults
    #----------------------------------------------------------
    
    @api.model
    def _default_sidebar_type(self):
        return self.env.user.company_id.default_sidebar_preference or 'small'
    
    @api.model
    def _default_chatter_position(self):
        return self.env.user.company_id.default_chatter_preference or 'sided'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    sidebar_type = fields.Selection(
        selection=[
            ('invisible', 'Invisible'),
            ('small', 'Small'),
            ('large', 'Large')
        ], 
        required=True,
        string="Sidebar Type",
        default=lambda self: self._default_sidebar_type())
    
    chatter_position = fields.Selection(
        selection=[
            ('normal', 'Normal'),
            ('sided', 'Sided'),
        ], 
        required=True,
        string="Chatter Position", 
        default=lambda self: self._default_chatter_position())
    
    #----------------------------------------------------------
    # Setup
    #----------------------------------------------------------

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(['sidebar_type'])
        type(self).SELF_WRITEABLE_FIELDS.extend(['chatter_position'])
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(['sidebar_type'])
        type(self).SELF_READABLE_FIELDS.extend(['chatter_position'])
        return init_res
