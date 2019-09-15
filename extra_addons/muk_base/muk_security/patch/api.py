###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Security 
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

import logging

from odoo import models, api, SUPERUSER_ID

from odoo.addons.muk_utils.tools import patch
from odoo.addons.muk_security.tools import security

_logger = logging.getLogger(__name__)

@api.model
@patch.monkey_patch(api.Environment)
def __call__(self, cr=None, user=None, context=None):
    env = __call__.super(self, cr, user, context)
    if user and isinstance(user, security.NoSecurityUid):
        env.uid = user
        return env
    return env