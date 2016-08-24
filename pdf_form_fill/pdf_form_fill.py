# -*- coding: utf-8 -*-
# © initOS GmbH 2013
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
try:
    from fdfgen import forge_fdf
except ImportError:
    forge_fdf = False
from openerp.osv import orm
from openerp.tools.translate import _
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
            _(u'Not implemented Error'),
            _(u'There is no file path method for the given model.')
        )

    def download_pdf_form(self, cr, uid, ids,
                          field_name=None, arg=None, context=None):
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
        if not forge_fdf:
            raise orm.except_orm(
                _(u'Missing fdfgen library.'),
                _(u'You need to install python fdfgen library.')
            )
        try:
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
        finally:
            os.remove(fdf_file.name)  # remove the temp file after we use it

        result = {}
        result[ids[0]] = base64.encodestring(outpu_file.read())
        fdf_file.close()
        return result
