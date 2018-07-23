# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
from base64 import b64encode

from odoo import api, fields, models


class Py3oTemplate(models.Model):
    _name = 'py3o.template'

    name = fields.Char(required=True)
    py3o_template_data = fields.Binary("LibreOffice Template")
    filetype = fields.Selection(
        selection=[
            ('odt', "ODF Text Document"),
            ('ods', "ODF Spreadsheet"),
            ('odp', "ODF Presentation"),
            ('fodt', "ODF Text Document (Flat)"),
            ('fods', "ODF Spreadsheet (Flat)"),
            ('fodp', "ODF Presentation (Flat)"),
        ],
        string="LibreOffice Template File Type",
        required=True,
        default='odt')

    # For filling the template data into the DB, it is no possible to
    # add directly the template in the xml data

    @api.model
    def fill_model(self, vals):
        actual_path = os.path.dirname(os.path.relpath(__file__))
        report_path = vals['path']
        report_path = "".join((actual_path, report_path))
        vals.pop('path', None)
        with open(report_path, 'rb') as f:
            vals.update({'py3o_template_data': b64encode(f.read())})

        rec = self.env.ref(vals['record'])
        vals.pop('record', None)
        rec.write(vals)
