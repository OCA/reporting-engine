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

class Base(models.AbstractModel):
    
    _inherit = 'base'

    @api.multi
    def refresh_views(self, model=None, ids=None, user=None, create=False):
        """ Informs the web client to refresh the views that belong to the 
            corresponding model by sending a message to the bus.
            
            There are two ways to use this method. First by calling it
            without any parameters. In this case, the views are determined
            and updated using the current records in self. Alternatively,
            the method can also be called with corresponding parameters
            to explicitly update a view from another model.
            
            :param model: The model of the records is used to find the
                corresponding views
            :param ids: IDs of the records are used to determine which
                records have been updated
            :param user: The user (res.users) is used to determine whether
                the current one has caused the refresh
            :param create: Indicates whether the record has been newly
                created or updated
        """
        if self.exists() or ids:
            record = next(iter(self)) if len(self) > 1 else self
            self.env['bus.bus'].sendone('refresh', {
                'create': create if ids else record.exists() and record.create_date == record.write_date or False,
                'model': model or self._name,
                'uid': user and user.id or False if ids else self.env.user.id,
                'ids': ids or self.mapped('id')})
