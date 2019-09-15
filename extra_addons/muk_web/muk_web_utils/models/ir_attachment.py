###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Web Utils 
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

import base64
import logging
import mimetypes

from odoo import api, models, fields, _
from odoo.exceptions import AccessError
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    
    _inherit = 'ir.attachment'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    temporary = fields.Boolean(
        string="Temporary",
        default=False,
        help="Attachments will be deleted by Autovacuum.",
    )
    