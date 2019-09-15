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

class BaseAutomation(models.Model):
    
    _inherit = 'base.automation'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.model
    def create_refresh_rules(self, model_name):
        model = self.env['ir.model'].search(
            [('model', '=', model_name)], limit=1)
        if model_name in self.env and model:
            triggers = [
                ('on_create', 'Creation'),
                ('on_write', 'Update'),
                ('on_unlink', 'Deletion')
            ]
            for trigger in triggers:
                refresh_rules = self.search([
                    ('model_id', '=', model.id),
                    ('trigger', '=', trigger[0])
                ], limit=1)
                if len(refresh_rules) > 0:
                    refresh_rules.write({
                        'active': True
                    })
                else:
                    self.create({
                        'trigger': trigger[0],
                        'state': 'refresh',
                        'model_id': model.id,
                        'name': "Refresh %s on %s" % (
                            model.name,
                            trigger[1]
                        )
                    })