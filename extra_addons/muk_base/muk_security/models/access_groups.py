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

from odoo import models, fields, api

class AccessGroups(models.Model):
    
    _name = 'muk_security.access_groups'
    _description = "Record Access Groups"
    _inherit = 'muk_utils.mixins.groups'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    perm_read = fields.Boolean(
        string='Read Access')
    
    perm_create = fields.Boolean(
        string='Create Access')
    
    perm_write = fields.Boolean(
        string='Write Access')
    
    perm_unlink = fields.Boolean(
        string='Unlink Access')
 