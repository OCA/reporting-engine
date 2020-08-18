# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    full_header_img = fields.Binary(
        string="Full header image",
        help="This image will replace all header.",
        attachment=True,
    )
    full_footer_img = fields.Binary(
        string="Full footer image",
        help="This image will replace all footer.",
        attachment=True,
    )
