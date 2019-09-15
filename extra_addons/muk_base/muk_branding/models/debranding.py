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

from odoo import models, fields, api

from odoo.addons.muk_branding.tools.debrand import safe_debrand

class Debranding(models.AbstractModel):
    
    _name = 'muk_branding.debranding'
    _description = 'Debranding'
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _get_debrand_params(self):
        return self.env['ir.config_parameter'].get_branding_debrand_params()
        
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def debrand(self, input, expression="odoo", context=None):
        context = context or self.env.context
        if 'no_debranding' in context:
            return input
        return safe_debrand(input, self._get_debrand_params(), expression=expression)