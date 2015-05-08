# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2013 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from fdfgen import forge_fdf
from tempfile import NamedTemporaryFile
import subprocess
import base64
import os


class pdf_form_fill(orm.Model):
    _name = 'pdf.form.fill'

    def get_directory_name(self):
        return os.path.dirname(__file__)

    def prepare_pdf_fields(self, cr, uid, ids, context=None):
        """Overwrite this to add specific preparations.
           Return value has to be a list of tupel ('pdf field name', value)
        """
        return []

    def get_pdf_file_path(self, cr, uid, ids, context=None):
        """Overwrite this to return the specific pdf file path."""
        raise orm.except_orm(
            (u'Not implemented Error'),
            (u'There is no file path method for the given model.')
        )

    def download_pdf_form(self, cr, uid, ids, context=None):
        file_path = self.get_pdf_file_path(cr, uid, ids, context=context)
        fields = self.prepare_pdf_fields(cr, uid, ids, context=context)

        # iterate through all fields to change FALSE values to ''
        def _transform_field(x):
            k, v = x
            if v is False:
                return (k, '')
            return (k, v)
        fields = map(_transform_field, fields)

        # create the fdf file for filling the form
        fdf = forge_fdf("", fields, [], [], [])
        fdf_file = NamedTemporaryFile(mode='wb', delete=False)
        fdf_file.write(fdf)
        fdf_file.close()

        outpu_file = NamedTemporaryFile(mode='r+')
        subprocess.call(['pdftk',
                         file_path,
                         'fill_form',
                         fdf_file.name,
                         'output',
                         outpu_file.name,
                         'flatten'])
        os.remove(fdf_file.name)  # remove the temp file after we use it

        result = {}
        result[ids[0]] = base64.encodestring(outpu_file.read())
        fdf_file.close()
        return result
