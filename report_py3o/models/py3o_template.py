# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Py3oTemplate(models.Model):
    _name = "py3o.template"
    _description = "Py3o template"

    name = fields.Char(required=True)
    py3o_template_data = fields.Binary("LibreOffice Template")
    filetype = fields.Selection(
        selection=[
            ("odt", "ODF Text Document"),
            ("ods", "ODF Spreadsheet"),
            ("odp", "ODF Presentation"),
            ("fodt", "ODF Text Document (Flat)"),
            ("fods", "ODF Spreadsheet (Flat)"),
            ("fodp", "ODF Presentation (Flat)"),
        ],
        string="LibreOffice Template File Type",
        required=True,
        default="odt",
    )
