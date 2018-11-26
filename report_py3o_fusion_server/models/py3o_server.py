# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Py3oServer(models.Model):
    _name = 'py3o.server'
    _description = 'Py3o server'
    _rec_name = 'url'

    url = fields.Char(
        "Py3o Fusion Server URL", required=True,
        help="If your Py3o Fusion server is on the same machine and runs "
        "on the default port, the URL is http://localhost:8765/form")
    is_active = fields.Boolean("Active", default=True)
    pdf_options_id = fields.Many2one(
        'py3o.pdf.options', string='PDF Options', ondelete='restrict',
        help="PDF options can be set per Py3o Server but also per report. "
        "If both are defined, the options on the report are used.")
