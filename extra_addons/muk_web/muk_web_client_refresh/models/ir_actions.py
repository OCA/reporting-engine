###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Refresh 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import logging

from odoo import api, models, fields

_logger = logging.getLogger(__name__)

class ServerActions(models.Model):
    
    _inherit = 'ir.actions.server'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    state = fields.Selection(
        selection_add=[('refresh', 'Refresh Views')])
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
        
    @api.model
    def run_action_refresh_multi(self, action, eval_context={}):
        if not self.env.context.get('refresh_disable', False):
            record = eval_context.get('record', None)
            records = eval_context.get('records', None)
            self.env['bus.bus'].sendone('refresh', {
                'uid': self.env.uid,
                'model': action.model_name,
                'ids': list(set().union(record and record.ids or [], records and records.ids or [])),
                'create': record and record.exists() and record.create_date == record.write_date,
            })