###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Notification 
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

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class NotifyWizard(models.TransientModel):
    
    _name = "muk_web_client_notification.send_notifications"
    
    def _default_user_ids(self):
        user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
        return [(6, 0, user_ids)]
    
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='muk_web_client_notification_user_rel',
        column1='wizard_id',
        column2='user_id',
        string='Users',
        default=_default_user_ids,
        help="If no user is selected, the message is sent globally to all users.")
    
    type = fields.Selection(
        selection=[('info', 'Information'), ('warning', 'Warning')],
        string='Type',
        required=True,
        default='info')
    
    title = fields.Char(
        string="Title",
        required=True)
    
    message = fields.Text(
        string="Message",
        required=True)
    
    sticky = fields.Boolean(
        string="Sticky")
    
    action_id = fields.Many2one(
        comodel_name='ir.actions.act_window',
        string='Action',
        help="If an action is set a button to call it is added to the notification.")
    
    close = fields.Boolean(
        string="Close",
        default=True)
    
    @api.multi
    def send_notifications(self):
        for record in self:
            params = {
                'type': record.type,
                'title': record.title,
                'message': record.message,
                'sticky': record.sticky,
            }
            if record.action_id.exists():
                buttons = [{
                    'text': _("Action"),
                    'primary': True,
                    'action': record.action_id.id,
                }]
                if record.close:
                    buttons.append({
                        'text': _("Close"),
                        'primary': False,
                        'action': None,
                    })
                params.update({'buttons': buttons})
            record.user_ids.notify(**params)
        return {
            'type': 'ir.actions.act_window_close'
        }
        
    @api.onchange('action_id')
    def check_change(self):
        if self.action_id:
            self.sticky = True