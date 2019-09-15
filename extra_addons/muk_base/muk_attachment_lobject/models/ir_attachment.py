###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Large Objects Attachment 
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

import base64
import logging
import mimetypes

from odoo import api, models, _
from odoo.exceptions import AccessError

from odoo.addons.muk_fields_lobject.fields.lobject import LargeObject

_logger = logging.getLogger(__name__)

class LObjectIrAttachment(models.Model):
    
    _inherit = 'ir.attachment'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    store_lobject = LargeObject(
        string="Data")
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _get_datas_inital_vals(self):
        vals = super(LObjectIrAttachment, self)._get_datas_inital_vals()
        vals.update({'store_lobject': False})
        return vals
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
    
    @api.model
    def storage_locations(self):
        locations = super(LObjectIrAttachment, self).storage_locations()
        locations.append('lobject')
        return locations
    
    @api.model
    def force_storage(self):
        if not self.env.user._is_admin():
            raise AccessError(_('Only administrators can execute this action.'))
        if self._storage() != 'lobject':
            return super(LObjectIrAttachment, self).force_storage()
        else:
            storage_domain = {
                'lobject': ('store_lobject', '=', False),
            }
            record_domain = [
                '&', ('type', '=', 'binary'),
                '&', storage_domain[self._storage()], 
                '|', ('res_field', '=', False), ('res_field', '!=', False)
            ]
            self.search(record_domain).migrate(batch_size=100)
            return True
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('store_lobject')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        for attach in self:
            if attach.store_lobject:
                if bin_size:
                    attach.datas = attach.with_context({'human_size': True}).store_lobject
                else:
                    attach.datas = attach.with_context({'base64': True}).store_lobject
            else:
                super(LObjectIrAttachment, attach)._compute_datas()
        
    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------
    
    @api.multi
    def _inverse_datas(self):
        location = self._storage()
        if location == 'lobject':
            for attach in self:
                value = attach.datas
                bin_data = base64.b64decode(value) if value else b''
                vals = self._get_datas_inital_vals()
                vals = self._update_datas_vals(vals, attach, bin_data)
                vals['store_lobject'] = bin_data
                clean_vals = self._get_datas_clean_vals(attach)
                models.Model.write(attach.sudo(), vals)
                self._clean_datas_after_write(clean_vals)
        else:
            super(LObjectIrAttachment, self)._inverse_datas()