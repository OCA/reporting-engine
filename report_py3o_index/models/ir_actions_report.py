# Copyright 2024 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class IrActionsReport(models.Model):

    _inherit = 'ir.actions.report'
    py3o_has_index_fallback = fields.Boolean(
        "Has Py3o Index? (Fallback)",
        default=False,
        help="Check if the template fallback has a py3o index. "
             "It needs to be compiled twice to get the index right."
    )
