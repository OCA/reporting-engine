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
import uuid
import logging
import mimetypes

from odoo import _, api, fields, models

# from odoo.addons.muk_utils.tools.http import get_response TODO
#from odoo.addons.muk_converter.tools import converter

_logger = logging.getLogger(__name__)

class ConverterWizard(models.TransientModel):
    
    _name = "muk_converter.convert"
    
    #----------------------------------------------------------
    # Selections
    #----------------------------------------------------------
    
    def _format_selection(self):
        formats = self.env['muk_converter.converter'].formats()
        return list(map(lambda format: (format, format.upper()), formats))
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    state = fields.Selection(
        selection=[
            ("export", "Export"),
            ("download", "Download")],
        string="State",
        required=True,
        default="export")
     
    input_name = fields.Char(
        string="Filename",
        states={'export': [('required', True)]})
    
    input_binary = fields.Binary(
        string="File",
        attachment=False,
        states={'export': [('required', True)]})
    
    format = fields.Selection(
        selection=_format_selection,
        string="Format",
        default="pdf",
        states={'export': [('required', True)]})
     
    output_name = fields.Char(
        string="Filename",
        readonly=True,
        states={'download': [('required', True)]})
    
    output_binary = fields.Binary(
        string="File",
        readonly=True,
        attachment=False,
        states={'download': [('required', True)]})
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def convert(self):
        self.ensure_one()
        name = "%s.%s" % (os.path.splitext(self.input_name)[0], self.format)
        output = self.env['muk_converter.converter'].convert(self.input_name, self.input_binary)
        self.write({
            'state': 'download',
            'output_name': name,
            'output_binary': output})
        return {
            "name": _("Convert File"),
            'type': 'ir.actions.act_window',
            'res_model': 'muk_converter.convert',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }