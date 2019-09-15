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

import logging

from odoo import api, models, fields

from odoo.addons.muk_fields_lobject.fields.lobject import LargeObject

_logger = logging.getLogger(__name__)

class Store(models.Model):
    
    _name = 'muk_converter.store'
    _description = 'Converter Store'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------

    name = fields.Char(
        compute="_compute_name",
        string="Name",
        store=True)

    used_date = fields.Datetime(
        string="Used on",
        default=fields.Datetime.now)
    
    checksum = fields.Char(
        string="Checksum",
        required=True)
    
    format = fields.Char(
        string="Format",
        required=True)

    content_fname = fields.Char(
        string="Filename",
        required=True)
    
    content = LargeObject(
        string="Data",
        required=True)
   
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
   
    @api.depends('checksum', 'content_fname')
    def _compute_name(self):
        for record in self:
            record.name = "%s (%s)" % (record.content_fname, record.checksum)
