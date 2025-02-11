from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # === Misc Information === #
    blocked = fields.Boolean(
        string='No Follow-up',
        default=False,
        help="You can check this box to mark this journal item as a litigation with the "
            "associated partner",
    )
