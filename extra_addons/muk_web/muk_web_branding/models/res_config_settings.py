###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Branding 
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

PRIMARY_XML_ID = "muk_web_branding._assets_primary_variables"
PRIMARY_SCSS_URL = "/muk_web_branding/static/src/scss/primary_colors.scss"

SECONDARY_XML_ID = "muk_web_branding._assets_secondary_variables"
SECONDARY_SCSS_URL = "/muk_web_branding/static/src/scss/secondary_colors.scss"

BOOTSTRAP_XML_ID = "muk_web_branding._assets_backend_helpers"
BOOTSTRAP_SCSS_URL = "/muk_web_branding/static/src/scss/bootstrap_colors.scss"

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    branding_color_brand = fields.Char(
        string="Brand Color")
    
    branding_color_primary = fields.Char(
        string="Primary Color")
    
    branding_color_secondary = fields.Char(
        string="Secondary Color")
    
    branding_color_lightsecondary = fields.Char(
        string="Light Secondary Color")
    
    branding_color_text = fields.Char(
        string="Text Color")
    
    branding_color_muted = fields.Char(
        string="Muted Color")
    
    branding_color_view = fields.Char(
        string="View Color")
    
    branding_color_background = fields.Char(
        string="Form Color")
    
    branding_color_notification_error = fields.Char(
        string="Notification Error Color")
    
    branding_color_notification_info = fields.Char(
        string="Notification Info Color")
    
    branding_color_01 = fields.Char(
        string="Color 01")
    
    branding_color_02 = fields.Char(
        string="Color 02")
    
    branding_color_03 = fields.Char(
        string="Color 03")
    
    branding_color_04 = fields.Char(
        string="Color 04")
    
    branding_color_05 = fields.Char(
        string="Color 05")
    
    branding_color_06 = fields.Char(
        string="Color 06")
    
    branding_color_07 = fields.Char(
        string="Color 07")
    
    branding_color_08 = fields.Char(
        string="Color 08")
    
    branding_color_09 = fields.Char(
        string="Color 09")
    
    branding_color_10 = fields.Char(
        string="Color 10")
    
    branding_color_11 = fields.Char(
        string="Color 11")
    
    branding_color_12 = fields.Char(
        string="Color 12")
    
    branding_color_success = fields.Char(
        string="Success Color")
    
    branding_color_info = fields.Char(
        string="Info Color")
    
    branding_color_warning = fields.Char(
        string="Warning Color")
    
    branding_color_danger = fields.Char(
        string="Danger Color")
    
    branding_color_light = fields.Char(
        string="Light Color")
    
    branding_color_dark = fields.Char(
        string="Dark Color")

    branding_color_white = fields.Char(
        string="White Color")
    
    branding_color_black = fields.Char(
        string="Black Color")
    
    branding_color_gray_100 = fields.Char(
        string="Gray 100 Color")
    
    branding_color_gray_200 = fields.Char(
        string="Gray 200 Color")
    
    branding_color_gray_300 = fields.Char(
        string="Gray 300 Color")
    
    branding_color_gray_400 = fields.Char(
        string="Gray 400 Color")
    
    branding_color_gray_500 = fields.Char(
        string="Gray 500 Color")
    
    branding_color_gray_600 = fields.Char(
        string="Gray 600 Color")
    
    branding_color_gray_700 = fields.Char(
        string="Gray 700 Color")
    
    branding_color_gray_800 = fields.Char(
        string="Gray 800 Color")
    
    branding_color_gray_900 = fields.Char(
        string="Gray 900 Color")
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _get_branding_primary_colors(self):
        variables = [
            'o-community-color',
            'o-enterprise-color',
            'o-enterprise-primary-color',
            'o-brand-odoo',
            'o-brand-primary',
            'o-gray',
            'o-brand-secondary',
            'o-brand-lightsecondary',
            'o-main-text-color',
            'o-main-color-muted',
            'o-view-background-color',
            'o-notification-error-bg-color',
            'o-notification-info-bg-color',
        ]
        colors = self.env['muk_utils.scss_editor'].get_values(
            PRIMARY_SCSS_URL, PRIMARY_XML_ID, variables
        )
        if colors['o-brand-odoo'] == '$o-community-color':
            colors['o-brand-odoo'] = colors['o-community-color']
        if colors['o-brand-odoo'] == '$o-enterprise-color':
            colors['o-brand-odoo'] = colors['o-enterprise-color']
        if colors['o-brand-primary'] == '$o-community-color':
            colors['o-brand-primary'] = colors['o-community-color']
        if colors['o-brand-primary'] == '$o-enterprise-primary-color':
            colors['o-brand-primary'] = colors['o-enterprise-primary-color']
        if colors['o-brand-secondary'] == '$o-gray-100':
            colors['o-brand-secondary'] = colors['o-gray-100']
        if colors['o-brand-lightsecondary'] == '$o-gray-100':
            colors['o-brand-lightsecondary'] = colors['o-gray-100']
        if colors['o-brand-lightsecondary'] == '$o-gray-100':
            colors['o-brand-lightsecondary'] = colors['o-gray-100']
        return {
            'branding_color_brand': colors['o-brand-odoo'],
            'branding_color_primary': colors['o-brand-primary'],
            'branding_color_secondary': colors['o-brand-secondary'],
            'branding_color_lightsecondary': colors['o-brand-lightsecondary'],
            'branding_color_text': colors['o-main-text-color'],
            'branding_color_muted': colors['o-main-color-muted'],
            'branding_color_view': colors['o-view-background-color'],
            'branding_color_notification_error': colors['o-notification-error-bg-color'],
            'branding_color_notification_info': colors['o-notification-info-bg-color'],
        }
    
    def _get_branding_secondary_colors(self):
        variables = [
            'o-webclient-background-color',
            'mk-color-01',
            'mk-color-02',
            'mk-color-03',
            'mk-color-04',
            'mk-color-05',
            'mk-color-06',
            'mk-color-07',
            'mk-color-08',
            'mk-color-09',
            'mk-color-10',
            'mk-color-11',
            'mk-color-12',
        ]
        colors = self.env['muk_utils.scss_editor'].get_values(
            SECONDARY_SCSS_URL, SECONDARY_XML_ID, variables
        )
        return {
            'branding_color_background': colors['o-webclient-background-color'],
            'branding_color_01': colors['mk-color-01'],
            'branding_color_02': colors['mk-color-02'],
            'branding_color_03': colors['mk-color-03'],
            'branding_color_04': colors['mk-color-04'],
            'branding_color_05': colors['mk-color-05'],
            'branding_color_06': colors['mk-color-06'],
            'branding_color_07': colors['mk-color-07'],
            'branding_color_08': colors['mk-color-08'],
            'branding_color_09': colors['mk-color-09'],
            'branding_color_10': colors['mk-color-10'],
            'branding_color_11': colors['mk-color-11'],
            'branding_color_12': colors['mk-color-12'],
        }
    
    def _get_branding_bootstrap_colors(self):
        variables = [
            'success',
            'info',
            'warning',
            'danger',
            'light',
            'dark',
            'white',
            'black',
            'gray-100',
            'gray-200',
            'gray-300',
            'gray-400',
            'gray-500',
            'gray-600',
            'gray-700',
            'gray-800',
            'gray-900',
        ]
        colors = self.env['muk_utils.scss_editor'].get_values(
            BOOTSTRAP_SCSS_URL, BOOTSTRAP_XML_ID, variables
        )
        return {
            'branding_color_success': colors['success'],
            'branding_color_info': colors['info'],
            'branding_color_warning': colors['warning'],
            'branding_color_danger': colors['danger'],
            'branding_color_light': colors['light'],
            'branding_color_dark': colors['dark'],
            'branding_color_white': colors['white'],
            'branding_color_black': colors['black'],
            'branding_color_gray_100': colors['gray-100'],
            'branding_color_gray_200': colors['gray-200'],
            'branding_color_gray_300': colors['gray-300'],
            'branding_color_gray_400': colors['gray-400'],
            'branding_color_gray_500': colors['gray-500'],
            'branding_color_gray_600': colors['gray-600'],
            'branding_color_gray_700': colors['gray-700'],
            'branding_color_gray_800': colors['gray-800'],
            'branding_color_gray_900': colors['gray-900'],
        }
        
    def _check_branding_colors(self, colors, variables):
        for values in variables:
            if colors[values['field']] != values['value']:
                return True
        return False
    
    def _set_branding_primary_colors(self):
        variables = [{
            'name': 'o-brand-odoo',
            'field': 'branding_color_brand',
            'value': self.branding_color_brand or "#7C7BAD"
        }, {
            'name': 'o-brand-primary',
            'field': 'branding_color_primary',
            'value': self.branding_color_primary or "#7C7BAD"
        }, {
            'name': 'o-brand-secondary',
            'field': 'branding_color_secondary',
            'value': self.branding_color_secondary or "#f0eeee"
        }, {
            'name': 'o-brand-lightsecondary',
            'field': 'branding_color_lightsecondary',
            'value': self.branding_color_lightsecondary or "#e2e2e0"
        }, {
            'name': 'o-main-text-color',
            'field': 'branding_color_text',
            'value': self.branding_color_text or "#4c4c4c"
        }, {
            'name': 'o-main-color-muted',
            'field': 'branding_color_muted',
            'value': self.branding_color_muted or "#a8a8a8"
        }, {
            'name': 'o-view-background-color',
            'field': 'branding_color_view',
            'value': self.branding_color_view or "#ffffff"
        }, {
            'name': 'o-notification-error-bg-color',
            'field': 'branding_color_notification_error',
            'value': self.branding_color_notification_error or "#F16567"
        }, {
            'name': 'o-notification-info-bg-color', 
            'field': 'branding_color_notification_info', 
            'value': self.branding_color_notification_info or "#FCFBEA"
        }]
        colors = self._get_branding_primary_colors()
        if self._check_branding_colors(colors, variables):
            self.env['muk_utils.scss_editor'].replace_values(
                PRIMARY_SCSS_URL, PRIMARY_XML_ID, variables
            )
    
    def _set_branding_secondary_colors(self):
        variables = [{
            'name': 'o-webclient-background-color',
            'field': 'branding_color_background',
            'value': self.branding_color_background or "#f9f9f9"
        }, {
            'name': 'mk-color-01',
            'field': 'branding_color_01',
            'value': self.branding_color_01 or "#757575"
        }, {
            'name': 'mk-color-02',
            'field': 'branding_color_02',
            'value': self.branding_color_02 or "#F06050"
        }, {
            'name': 'mk-color-03',
            'field': 'branding_color_03',
            'value': self.branding_color_03 or "#F4A460"
        }, {
            'name': 'mk-color-04',
            'field': 'branding_color_04',
            'value': self.branding_color_04 or "#F7CD1F"
        }, {
            'name': 'mk-color-05',
            'field': 'branding_color_05',
            'value': self.branding_color_05 or "#6CC1ED"
        }, {
            'name': 'mk-color-06',
            'field': 'branding_color_06',
            'value': self.branding_color_06 or "#814968"
        }, {
            'name': 'mk-color-07',
            'field': 'branding_color_07',
            'value': self.branding_color_07 or "#EB7E7F"
        }, {
            'name': 'mk-color-08',
            'field': 'branding_color_08',
            'value': self.branding_color_08 or "#2C8397"
        }, {
            'name': 'mk-color-09',
            'field': 'branding_color_09',
            'value': self.branding_color_09 or "#475577"
        }, {
            'name': 'mk-color-10',
            'field': 'branding_color_10',
            'value': self.branding_color_10 or "#D6145F"
        }, {
            'name': 'mk-color-11',
            'field': 'branding_color_11',
            'value': self.branding_color_11 or "#30C381"
        }, {
            'name': 'mk-color-12',
            'field': 'branding_color_12',
            'value': self.branding_color_12 or "#9365B8"
        }]
        colors = self._get_branding_secondary_colors()
        if self._check_branding_colors(colors, variables):
            self.env['muk_utils.scss_editor'].replace_values(
                SECONDARY_SCSS_URL, SECONDARY_XML_ID, variables
            )
            
    def _set_branding_bootstrap_colors(self):
        variables = [{
            'name': 'success',
            'field': 'branding_color_success',
            'value': self.branding_color_success or "#28a745"
        }, {
            'name': 'info',
            'field': 'branding_color_info',
            'value': self.branding_color_info or "#17a2b8"
        }, {
            'name': 'warning',
            'field': 'branding_color_warning',
            'value': self.branding_color_warning or "#ffc107"
        }, {
            'name': 'danger',
            'field': 'branding_color_danger',
            'value': self.branding_color_danger or "#dc3545"
        }, {
            'name': 'light',
            'field': 'branding_color_light',
            'value': self.branding_color_light or "#f8f9fa"
        }, {
            'name': 'dark',
            'field': 'branding_color_dark',
            'value': self.branding_color_dark or "#343a40"
        }, {
            'name': 'white',
            'field': 'branding_color_white',
            'value': self.branding_color_white or "#ffffff"
        }, {
            'name': 'black',
            'field': 'branding_color_black',
            'value': self.branding_color_black or "#000000"
        }, {
            'name': 'gray-100',
            'field': 'branding_color_gray_100',
            'value': self.branding_color_gray_100 or "#f8f9fa"
        }, {
            'name': 'gray-200',
            'field': 'branding_color_gray_200',
            'value': self.branding_color_gray_200 or "#e9ecef"
        }, {
            'name': 'gray-300',
            'field': 'branding_color_gray_300',
            'value': self.branding_color_gray_300 or "#dee2e6"
        }, {
            'name': 'gray-400',
            'field': 'branding_color_gray_400',
            'value': self.branding_color_gray_400 or "#ced4da"
        }, {
            'name': 'gray-500',
            'field': 'branding_color_gray_500',
            'value': self.branding_color_gray_500 or "#adb5bd"
        }, {
            'name': 'gray-600',
            'field': 'branding_color_gray_600',
            'value': self.branding_color_gray_600 or "#6c757d"
        }, {
            'name': 'gray-700',
            'field': 'branding_color_gray_700',
            'value': self.branding_color_gray_700 or "#495057"
        }, {
            'name': 'gray-800',
            'field': 'branding_color_gray_800',
            'value': self.branding_color_gray_800 or "#343a40"
        }, {
            'name': 'gray-900',
            'field': 'branding_color_gray_900',
            'value': self.branding_color_gray_900 or "#212529"
        }]
        colors = self._get_branding_bootstrap_colors()
        if self._check_branding_colors(colors, variables):
            self.env['muk_utils.scss_editor'].replace_values(
                BOOTSTRAP_SCSS_URL, BOOTSTRAP_XML_ID, variables
            )        
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(self._get_branding_primary_colors())
        res.update(self._get_branding_secondary_colors())
        res.update(self._get_branding_bootstrap_colors())
        return res
    
    @api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self._set_branding_primary_colors()
        self._set_branding_secondary_colors()
        self._set_branding_bootstrap_colors()
        return res

    
    