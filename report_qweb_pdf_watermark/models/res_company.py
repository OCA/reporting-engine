# Copyright 2022 360 ERP (<https://www.360erp.nl>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    pdf_watermark = fields.Binary("Watermark")
