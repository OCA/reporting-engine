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

from odoo import models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.muk_utils.tools.utils import safe_execute

class IrActionsActWindow(models.Model):
    
    _inherit = 'ir.actions.act_window'

    def read(self, fields=None, load='_classic_read'):
        result = super(IrActionsActWindow, self).read(fields=fields, load=load)
        if not fields or 'help' in fields:
            for values in result:
                if isinstance(values, dict) and values.get('help'):
                    user_context = dict(self.env.context)
                    value_context = values.get('context', '{}')
                    context = safe_execute({}, safe_eval, value_context, user_context)
                    values['help'] = self.env['muk_branding.debranding'].debrand(values['help'])
        return result
