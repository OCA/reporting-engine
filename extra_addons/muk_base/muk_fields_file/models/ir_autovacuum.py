###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Filestore Field 
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

import time
import logging
import datetime
import dateutil

from odoo import _
from odoo import models, api, fields
from odoo.tools.safe_eval import safe_eval

from odoo.addons.muk_fields_file.fields import file

_logger = logging.getLogger(__name__)

class AutoVacuum(models.AbstractModel):
    
    _inherit = 'ir.autovacuum'
    
    @api.model
    def power_on(self, *args, **kwargs):
        res = super(AutoVacuum, self).power_on(*args, **kwargs)
        file.clean_store(self.env.cr.dbname, self.env)
        return res