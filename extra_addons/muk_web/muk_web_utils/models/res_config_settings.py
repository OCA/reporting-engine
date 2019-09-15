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

import re
import json
import logging

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    binary_max_size = fields.Integer(
        string='File Size Limit',
        required=True,
        default=25,
        help="""Maximum allowed file size in megabytes. Note that this setting only adjusts
            the binary widgets accordingly. The maximum file size on your server can probably
            be restricted in several places. Note that a large file size limit and therefore
            large files in your system can significantly limit performance.""")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('muk_web_utils.binary_max_size', self.binary_max_size)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(binary_max_size=int(params.get_param('muk_web_utils.binary_max_size', 25)))
        return res
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        ret_val = super(ResConfigSettings, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        modules = self.env['ir.module.module'].sudo().search([]).mapped('name')
        document = etree.XML(ret_val['arch'])
        for field in ret_val['fields']:
            if field.startswith("module_") and field[len("module_"):] not in modules:
                for node in document.xpath("//field[@name='%s']" % field):
                    if node.get("widget") != 'upgrade_boolean':
                        node.set("widget", "module_boolean")
        ret_val['arch'] = etree.tostring(document, encoding='unicode')
        return ret_val