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

from odoo import _, api, models

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):

    _inherit = 'res.users'
    
    @api.multi
    def notify(self, **params):
        """ Informs the web client to refresh the views that belong to the 
            corresponding model by sending a message to the bus.
            
            There are two ways to use this method. First by calling it
            without any parameters. In this case, the views are determined
            and updated using the current records in self. Alternatively,
            the method can also be called with corresponding parameters
            to explicitly update a view from another model.
            
            :param title: The notification title
            :param message: The notification main message 
            :param type: Either 'notification' or 'warning'
            :param sticky: Determines if the notification is sticky
            :param buttons: List of buttons, which consists of:
                text: The buttons text
                primary: Determines if the button is primary
                icon: The buttons font-awsome className or image src
                action: Either an action id, a descriptor or False to 
                    just to close the notification on the button click
        """
        params.update({'user_ids': self.ids})
        self.env['bus.bus'].sendone('notify', params)
        
    @api.multi
    def notify_info(self, message, title=None, sticky=False):
        self.notify(type='info', title=title or _('Information'), message=message, sticky=sticky)

    @api.multi
    def notify_warning(self, message, title=None, sticky=False):
        self.notify(type='warning', title=title or _('Warning'), message=message, sticky=sticky)
