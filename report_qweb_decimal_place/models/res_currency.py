# Copyright 2022 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    apply_price_decimal_place = fields.Boolean(
        help="Apply this decimal place to the unit price field of relevant PDF reports "
        "where appropriate customization is done."
    )
    price_decimal_places = fields.Integer(
        help="Define decimal places for the unit price field of relevant PDF reports"
    )
