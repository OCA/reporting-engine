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

from odoo import api, SUPERUSER_ID

from . import controllers
from . import models

REFRESH_RULE_MODELS = [
    'account.bank.statement', 'account.invoice', 'account.journal', 
    'account.move', 'crm.lead', 'event.event', 'fleet.vehicle', 'hr.contract',
    'hr.department', 'hr.employee', 'hr.job', 'hr.leave', 'lunch.order',
    'mrp.bom', 'mrp.document', 'mrp.workorder', 'product.category',
    'product.template', 'project.project', 'project.task', 'purchase.order',
    'repair.order', 'res.partner', 'res.users', 'sale.order', 'slide.slide',
    'stock.inventory', 'stock.move', 'survey.page', 'survey.survey',
]

def _install_initialize_rules(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for model_name in REFRESH_RULE_MODELS:
        env['base.automation'].create_refresh_rules(model_name)
        
def _uninstall_remove_rules(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['base.automation'].search([('state', '=', 'refresh')]).unlink()
