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

import os
import re
import shutil
import base64
import hashlib
import logging
import binascii
import tempfile

from collections import defaultdict

from odoo import fields, tools
from odoo.tools import human_size, config

from odoo.addons.muk_utils.tools.file import ensure_path_directories

_logger = logging.getLogger(__name__)

def get_store_path(dbname):
    return os.path.join(config.get('data_dir'), 'files', dbname)

def clean_store(dbname, env):
    tables = defaultdict(set)
    for model_name in env.registry.models:
        model = env[model_name]
        if not model._abstract:
            for name, field in model._fields.items():
                if field.type == 'file':
                    tables[model._table].add(name)
    checklist = set()
    filestore = get_store_path(dbname)
    path = os.path.join(filestore, 'checklist')
    for root, dirs, files in os.walk(path):
        for file in files:
            checkpath = os.path.join(root, file)
            relpath = os.path.relpath(checkpath, path)
            checklist.add(os.path.join(filestore, relpath))
    env.cr.commit()
    whitelist = set()
    for table, fields in tables.items():
        select_fields = list(fields)
        env.cr.execute("LOCK %s IN SHARE MODE" % table)
        select_query = "SELECT {0}".format(', '.join(select_fields)) 
        where_query = "WHERE {0} IN %(paths)s".format(select_fields[0])
        if len(select_fields) > 1:
            for field in select_fields[:1]:
                where_query += "OR {0} IN %s".format(field)
        sql_query = "{0} FROM {1} {2};".format(select_query, table, where_query)
        for paths in env.cr.split_for_in_conditions(checklist):
            env.cr.execute(sql_query, {'paths': paths})
            for row in env.cr.fetchall():
                for column in row:
                    whitelist.add(column)       
    remove = checklist - whitelist
    for file in remove:
        try:
            os.unlink(file)
        except (OSError, IOError):
            _logger.warn("Deleting file from %s failed!", file, exc_info=True)
    with tools.ignore(OSError):
        shutil.rmtree(path)
    env.cr.commit()
    _logger.info("Cleaned files [ %d checked | %d removed ]", len(checklist), len(remove))

class File(fields.Field):
    
    type = 'file'
    column_type = ('varchar', 'varchar')
    _slots = {
        'prefetch': False,              
        'context_dependent': True,      
    }

    def _get_file_path(self, checksume, dbname):
        name =  os.path.join(checksume[:2], checksume)
        name = re.sub('[.]', '', name).strip('/\\')
        filestore = get_store_path(dbname)
        path = os.path.join(filestore, name)
        ensure_path_directories(path)
        return path 
    
    def _add_to_checklist(self, path, dbname):
        filestore = get_store_path(dbname)
        relpath = os.path.relpath(path, filestore)
        checklist = os.path.join(filestore, 'checklist', relpath)
        if not os.path.exists(checklist):
            ensure_path_directories(checklist)
            open(checklist, 'ab').close()

    def _get_checksum(self, value):
        if isinstance(value, bytes):
            return hashlib.sha1(value).hexdigest()
        else:
            checksum = hashlib.sha1()
            while True:
                chunk = value.read(4096)
                if not chunk:
                    return checksum.hexdigest()
                checksum.update(chunk)
                
    def convert_to_column(self, value, record, values=None, validate=True):
        path = None
        try:
            current_path = record.with_context({'path': True})[self.name]
            if current_path:
                self._add_to_checklist(current_path, record.env.cr.dbname)
            if not value:
                return None
            binary = None
            if isinstance(value, bytes):
                binary = value
            elif isinstance(value, str):
                binary = base64.b64decode(value)
            if binary:
                checksume = self._get_checksum(binary)
                path = self._get_file_path(checksume, record.env.cr.dbname)
                with open(path, 'wb') as file:
                    file.write(binary)
                self._add_to_checklist(path, record.env.cr.dbname)
            else:
                checksume = self._get_checksum(value)
                path = self._get_file_path(checksume, record.env.cr.dbname)
                value.seek(0, 0)
                with open(path, 'wb') as file:
                    while True:
                        chunk = value.read(4096)
                        if not chunk:
                            break
                        file.write(chunk)
                self._add_to_checklist(path)
        except (IOError, OSError):
            _logger.warn("Writing file to %s failed!", path, exc_info=True)
        return path

    def convert_to_record(self, value, record):
        if value and isinstance(value, str) and os.path.exists(value):
            try:
                with open(value, 'rb') as file:
                    if record._context.get('human_size'):
                        return human_size(file.seek(0, 2))
                    elif record._context.get('bin_size'):
                        return file.seek(0, 2)
                    elif record._context.get('path'):
                        return value
                    elif record._context.get('base64'):
                        return base64.b64encode(file.read())
                    elif record._context.get('stream'):
                        temp = tempfile.TemporaryFile()
                        while True:
                            chunk = file.read(4096)
                            if not chunk:
                                temp.seek(0)
                                return temp
                            temp.write(chunk)
                    elif record._context.get('checksum'):
                        checksum = hashlib.sha1()
                        while True:
                            chunk = file.read(4096)
                            if not chunk:
                                return checksum.hexdigest()
                            checksum.update(chunk)
                    else:
                        return file.read()
            except (IOError, OSError):
                _logger.warn("Reading file from %s failed!", value, exc_info=True)
        return value
    
    def convert_to_export(self, value, record):
        if value:
            try:
                with open(value, 'rb') as file:
                    if record._context.get('export_raw_data'):
                        return file.read()
                    return base64.b64encode(file.read())
            except (IOError, OSError):
                _logger.warn("Reading file from %s failed!", value, exc_info=True)
        return ''