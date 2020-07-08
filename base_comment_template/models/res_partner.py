# Copyright 2020 NextERP Romania SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    base_comment_template_ids = fields.Many2many(
        comodel_name="base.comment.template",
        string="Comment Templates",
        help="Specific partner comments that can be included in reports",
    )
