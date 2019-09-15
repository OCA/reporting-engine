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

import re
import uuid
import base64

from odoo import api, fields, models

XML_ID = "muk_web_theme._assets_primary_variables"
SCSS_URL = "/muk_web_theme/static/src/scss/colors.scss"

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    module_muk_web_theme_mail = fields.Boolean(
        string="Theme Mail",
        help="Optimizes the mail chatter for the theme.")
    
    module_muk_web_theme_branding = fields.Boolean(
        string="Theme Branding",
        help="Customize the theme according to your needs.")
    
    module_muk_web_theme_website = fields.Boolean(
        string="Theme Website",
        help="Add theme styled website navigation.")
    
    module_muk_web_theme_mobile = fields.Boolean(
        string="Theme Mobile",
        help="Allow Odoo to be used as a PWA app.")
    
    theme_background_image = fields.Binary(
        related="company_id.background_image",
        readonly=False)
    
    theme_background_blend_mode = fields.Selection(
        related="company_id.background_blend_mode",
        readonly=False)
    
    theme_default_sidebar_preference = fields.Selection(
        related="company_id.default_sidebar_preference",
        readonly=False)

    theme_default_chatter_preference = fields.Selection(
        related="company_id.default_chatter_preference",
        readonly=False)
    
    theme_color_brand = fields.Char(
        string="Theme Brand Color")
    
    theme_color_primary = fields.Char(
        string="Theme Primary Color")
    
    theme_color_required = fields.Char(
        string="Theme Required Color")
    
    theme_color_menu = fields.Char(
        string="Theme Menu Color")
    
    theme_color_appbar_color = fields.Char(
        string="Theme AppBar Color")
    
    theme_color_appbar_background = fields.Char(
        string="Theme AppBar Background")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        variables = [
            'o-brand-odoo',
            'o-brand-primary',
            'mk-required-color',
            'mk-apps-color',
            'mk-appbar-color',
            'mk-appbar-background',
        ]
        colors = self.env['muk_utils.scss_editor'].get_values(
            SCSS_URL, XML_ID, variables
        )
        colors_changed = []
        colors_changed.append(self.theme_color_brand != colors['o-brand-odoo'])
        colors_changed.append(self.theme_color_primary != colors['o-brand-primary'])
        colors_changed.append(self.theme_color_required != colors['mk-required-color'])
        colors_changed.append(self.theme_color_menu != colors['mk-apps-color'])
        colors_changed.append(self.theme_color_appbar_color != colors['mk-appbar-color'])
        colors_changed.append(self.theme_color_appbar_background != colors['mk-appbar-background'])
        if(any(colors_changed)):
            variables = [
                {'name': 'o-brand-odoo', 'value': self.theme_color_brand or "#243742"},
                {'name': 'o-brand-primary', 'value': self.theme_color_primary or "#5D8DA8"},
                {'name': 'mk-required-color', 'value': self.theme_color_required or "#d1dfe6"},
                {'name': 'mk-apps-color', 'value': self.theme_color_menu or "#f8f9fa"},
                {'name': 'mk-appbar-color', 'value': self.theme_color_appbar_color or "#dee2e6"},
                {'name': 'mk-appbar-background', 'value': self.theme_color_appbar_background or "#000000"},
            ]
            self.env['muk_utils.scss_editor'].replace_values(
                SCSS_URL, XML_ID, variables
            )
        param.set_param('muk_web_theme.background_blend_mode', self.theme_background_blend_mode)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        variables = [
            'o-brand-odoo',
            'o-brand-primary',
            'mk-required-color',
            'mk-apps-color',
            'mk-appbar-color',
            'mk-appbar-background',
        ]
        colors = self.env['muk_utils.scss_editor'].get_values(
            SCSS_URL, XML_ID, variables
        )
        res.update({
            'theme_color_brand': colors['o-brand-odoo'],
            'theme_color_primary': colors['o-brand-primary'],
            'theme_color_required': colors['mk-required-color'],
            'theme_color_menu': colors['mk-apps-color'],
            'theme_color_appbar_color': colors['mk-appbar-color'],
            'theme_color_appbar_background': colors['mk-appbar-background'],
            'theme_background_blend_mode': params.get_param('muk_web_theme.background_blend_mode', 'normal'),
        })
        return res