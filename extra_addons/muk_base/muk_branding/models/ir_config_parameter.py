###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Branding 
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

from odoo import _, models, api
from odoo.modules import get_resource_path
from odoo.tools import mute_logger, ormcache, config

BRANDING_PARAMS = {
    'muk_branding.system_name': config.get('branding_system_name', 'System'),
    'muk_branding.publisher': config.get('branding_publisher', 'Example'),
    'muk_branding.website': config.get('branding_website', 'https://www.example.com'),
    'muk_branding.documentation': config.get('branding_documentation', 'https://www.example.com'),
    'muk_branding.support': config.get('branding_support', 'https://www.example.com/support'),
    'muk_branding.store': config.get('branding_store', 'https://www.example.com/store'),
    'muk_branding.share': config.get('branding_share', 'https://www.example.com'),
}

class IrConfigParameter(models.Model):
    
    _inherit = 'ir.config_parameter'
    
    @api.model_cr
    @mute_logger('odoo.addons.base.models.ir_config_parameter')
    def init(self, force=False):
        super(IrConfigParameter, self).init(force=force)
        for key, value in BRANDING_PARAMS.items():
            if force or not self.sudo().search([('key', '=', key)]): 
                self.sudo().set_param(key, value() if callable(value) else value)
    
    @api.model
    def get_branding_param(self, key, default=""):
        return self.sudo().get_param(key, default=default) if key in BRANDING_PARAMS else None
    
    @api.model
    @ormcache()
    def get_branding_params(self):
        return {key: self.get_branding_param(key) for key in BRANDING_PARAMS}
    
    @api.model
    @ormcache()
    def get_branding_settings_params(self):
        return {
            'branding_system_name': self.get_branding_param('muk_branding.system_name'),
            'branding_publisher': self.get_branding_param('muk_branding.publisher'),
            'branding_website': self.get_branding_param('muk_branding.website'),
            'branding_documentation': self.get_branding_param('muk_branding.documentation'),
            'branding_support': self.get_branding_param('muk_branding.support'),
            'branding_store': self.get_branding_param('muk_branding.store'),
            'branding_share': self.get_branding_param('muk_branding.share'),
        }

    @api.model
    @ormcache()
    def get_branding_dashboard_params(self):
        return {
            'store': self.get_branding_param('muk_branding.store'),
            'share': self.get_branding_param('muk_branding.share'),
            'system': self.get_branding_param('muk_branding.system_name'),
            'publisher': self.get_branding_param('muk_branding.publisher'),
        }
    
    @api.model
    @ormcache()
    def get_branding_session_params(self):
        return {
            'muk_branding_system_name': self.get_branding_param('muk_branding.system_name'),
            'muk_branding_documentation': self.get_branding_param('muk_branding.documentation'),
            'muk_branding_website': self.get_branding_param('muk_branding.website'),
            'muk_branding_support': self.get_branding_param('muk_branding.support')
        }

    @api.model
    @ormcache()
    def get_branding_debrand_params(self):
        return {
            'system_name': self.get_branding_param('muk_branding.system_name'),
            'documentation': self.get_branding_param('muk_branding.documentation'),
            'website': self.get_branding_param('muk_branding.website'),
        }
