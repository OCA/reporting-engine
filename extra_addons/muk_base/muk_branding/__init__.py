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

from odoo import api, SUPERUSER_ID
from odoo.release import version_info
from odoo.tools import config, convert_file
from odoo.modules.module import get_module_resource

from . import models
from . import tools

#----------------------------------------------------------
# Patch System on Load
#----------------------------------------------------------

def _patch_system():
    from . import patch
    
#----------------------------------------------------------
# Hooks
#----------------------------------------------------------

def _install_debrand_system(cr, registry):
    if version_info[5] != 'e':
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['ir.module.module'].search([('to_buy', '=', True)]).unlink()
        
def _uninstall_rebrand_system(cr, registry):
    if version_info[5] != 'e':
        filename = get_module_resource('base', 'data', 'ir_module_module.xml')
        convert_file(cr, 'base', filename, {}, 'init', False, 'data', registry._assertion_report)
  

