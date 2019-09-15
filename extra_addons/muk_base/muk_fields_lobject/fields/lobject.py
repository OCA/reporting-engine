###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Large Objects Field 
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
import hashlib
import logging
import binascii
import tempfile

from odoo import fields
from odoo.tools import human_size

_logger = logging.getLogger(__name__)

class LargeObject(fields.Field):
    
    type = 'lobject'
    column_type = ('oid', 'oid')
    _slots = {
        'prefetch': False,              
        'context_dependent': True,      
    }
    
    def convert_to_column(self, value, record, values=None, validate=True):
        oid = record.with_context({'oid': True})[self.name]
        if oid:
            record.env.cr._cnx.lobject(oid, 'rb').unlink()
        if not value:
            return None
        lobject = record.env.cr._cnx.lobject(0, 'wb')
        if isinstance(value, bytes):
            lobject.write(value)
        elif isinstance(value, str):
            lobject.write(base64.b64decode(value))
        else:
            while True:
                chunk = value.read(4096)
                if not chunk:
                    break
                lobject.write(chunk)
        return lobject.oid

    def convert_to_record(self, value, record):
        if value and isinstance(value, int):
            lobject = record.env.cr._cnx.lobject(value, 'rb')
            if record._context.get('human_size'):
                return human_size(lobject.seek(0, 2))
            elif record._context.get('bin_size'):
                return lobject.seek(0, 2)
            elif record._context.get('oid'):
                return lobject.oid
            elif record._context.get('base64'):
                return base64.b64encode(lobject.read())
            elif record._context.get('stream'):
                file = tempfile.TemporaryFile()
                while True:
                    chunk = lobject.read(4096)
                    if not chunk:
                        file.seek(0)
                        return file
                    file.write(chunk)
            elif record._context.get('checksum'):
                checksum = hashlib.sha1()
                while True:
                    chunk = lobject.read(4096)
                    if not chunk:
                        return checksum.hexdigest()
                    checksum.update(chunk)
            else:
                return lobject.read()
        return value
    
    def convert_to_export(self, value, record):
        if value:
            lobject = record.env.cr._cnx.lobject(value, 'rb')
            if record._context.get('export_raw_data'):
                return lobject.read()
            return base64.b64encode(lobject.read())
        return ''