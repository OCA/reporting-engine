# Copyright 2023 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class IrUiViewCustom(models.Model):
    _inherit = "ir.ui.view.custom"

    user_id = fields.Many2one(required=False)
