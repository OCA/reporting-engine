###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Utils 
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
import io
import sys
import base64
import shutil
import urllib
import logging
import hashlib
import binascii
import tempfile
import mimetypes
import unicodedata

from odoo.tools import human_size
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# File Helper
#----------------------------------------------------------

def slugify(value, lower=True):
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = value.lower() if lower else value
    value = re.sub('[^\w\s-]', '', value)
    value = re.sub('[-\s]+', '-', value)
    return value.strip()

def check_name(name):
    tmp_dir = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp_dir, name), 'a').close()
    except IOError:
        return False
    finally:
        shutil.rmtree(tmp_dir)
    return True

def compute_name(name, suffix, escape_suffix):
    if escape_suffix:
        name, extension = os.path.splitext(name)
        return "%s(%s)%s" % (name, suffix, extension)
    else:
        return "%s(%s)" % (name, suffix)

def unique_name(name, names, escape_suffix=False):
    if not name in names:
        return name
    else:
        suffix = 1
        name = compute_name(name, suffix, escape_suffix)
        while name in names:
            suffix += 1
            name = compute_name(name, suffix, escape_suffix)
        return name 

def unique_files(files):
    ufiles = []
    unames = []
    for file in files:
        uname = unique_name(file[0], unames, escape_suffix=True)
        ufiles.append((uname, file[1]))
        unames.append(uname)
    return ufiles  

def guess_extension(filename=None, mimetype=None, binary=None):
    extension = filename and os.path.splitext(filename)[1][1:].strip().lower()
    if not extension and mimetype:
        extension = mimetypes.guess_extension(mimetype)[1:].strip().lower()
    if not extension and binary:
        mimetype = guess_mimetype(binary, default="")
        extension = mimetypes.guess_extension(mimetype)[1:].strip().lower()
    return extension

#----------------------------------------------------------
# System Helper
#----------------------------------------------------------

def ensure_path_directories(path):
    directory_path = os.path.dirname(path)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def remove_empty_directories(path):
    if not os.path.isdir(path):
        return
    entries = os.listdir(path)
    if len(entries) > 0:
        for entry in entries:
            subpath = os.path.join(path, entry)
            if os.path.isdir(subpath):
                self._remove_empty_directories(subpath)
    else:
        os.rmdir(path)