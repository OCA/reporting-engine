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
import json
import uuid
import logging
import shutil
import zipfile
import tempfile

from contextlib import closing

from odoo import _, modules, api, sql_db, SUPERUSER_ID
from odoo.tools import osutil, config, exec_pg_command
from odoo.service import db

from odoo.addons.muk_utils.tools import patch
from odoo.addons.muk_fields_file.fields import file

_logger = logging.getLogger(__name__)

@patch.monkey_patch(db)
@db.check_db_management_enabled
def exp_duplicate_database(db_original_name, db_name):
    res = exp_duplicate_database.super(db_original_name, db_name)
    from_files = file.get_store_path(db_original_name)
    to_files = file.get_store_path(db_name)
    if os.path.exists(from_files) and not os.path.exists(to_files):
        shutil.copytree(from_files, to_files)
    return res

@patch.monkey_patch(db)
@db.check_db_management_enabled
def exp_drop(db_name):
    res = exp_drop.super(db_name)
    files = file.get_store_path(db_name)
    if os.path.exists(files):
        shutil.rmtree(files)
    return res

@patch.monkey_patch(db)
@db.check_db_management_enabled
def dump_db(db_name, stream, backup_format='zip'):
    if backup_format == 'zip':
        res = dump_db.super(db_name, False, backup_format)
        with osutil.tempdir() as dump_dir:
            with zipfile.ZipFile(res, 'r') as zip:
                zip.extractall(dump_dir)
                files = file.get_store_path(db_name)
                if os.path.exists(files):
                    shutil.copytree(files, os.path.join(dump_dir, 'files'))
            if stream:
                osutil.zip_dir(dump_dir, stream, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
            else:
                t=tempfile.TemporaryFile()
                osutil.zip_dir(dump_dir, t, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t
    else:
        return dump_db.super(db_name, stream, backup_format)

@patch.monkey_patch(db)
@db.check_db_management_enabled
def restore_db(db, dump_file, copy=False):
    res = restore_db.super(db, dump_file, copy)
    with osutil.tempdir() as dump_dir:
        if zipfile.is_zipfile(dump_file):
            with zipfile.ZipFile(dump_file, 'r') as zip:
                files = [m for m in zip.namelist() if m.startswith('files/')]
                if files:
                    z.extractall(dump_dir, files)
                    files_path = os.path.join(dump_dir, 'files')
                    shutil.move(files_path, file.get_store_path(db_name))
    return res

@patch.monkey_patch(db)
@db.check_db_management_enabled
def exp_rename(old_name, new_name):
    res = exp_rename.super(old_name, new_name)
    from_files = file.get_store_path(old_name)
    to_files = file.get_store_path(new_name)
    if os.path.exists(from_files) and not os.path.exists(to_files):
        shutil.copytree(from_files, to_files)
    return res
