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

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    #----------------------------------------------------------
    # Selections
    #----------------------------------------------------------
    
    def _attachment_location_selection(self):
        locations = self.env['ir.attachment'].storage_locations()
        return list(map(lambda location: (location, location.upper()), locations))

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    attachment_location = fields.Selection(
        selection=lambda self: self._attachment_location_selection(),
        string='Storage Location',
        required=True,
        default='file',
        help="Attachment storage location.")
    
    attachment_location_changed = fields.Boolean(
        compute='_compute_attachment_location_changed',
        string='Storage Location Changed')
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('ir_attachment.location', self.attachment_location)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(attachment_location=params.get_param('ir_attachment.location', 'file'))
        return res
    
    def attachment_force_storage(self):
        self.env['ir.attachment'].force_storage()
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('attachment_location')
    def _compute_attachment_location_changed(self):
        params = self.env['ir.config_parameter'].sudo()
        location = params.get_param('ir_attachment.location', 'file')
        for record in self:
            record.attachment_location_changed = location != self.attachment_location
