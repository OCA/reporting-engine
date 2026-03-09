# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    report_positioned_image_ids = fields.Many2many(
        comodel_name="report.positioned.image",
        relation="res_company_positioned_image_rel",
        column1="company_id",
        column2="image_id",
        string="Company Images",
    )
