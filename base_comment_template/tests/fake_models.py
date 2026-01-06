# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE
# Copyright 2018 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class TestResUsers(models.Model):
    _name = "test.res.users"
    _description = "Test User"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["comment.template"]

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="restrict",
        bypass_search_access=True,
        index=True,
        string="Related Partner",
        help="Partner-related data of the user",
    )
    login = fields.Char(required=True, help="Used to log into the system")
