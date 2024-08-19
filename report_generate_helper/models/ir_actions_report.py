# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.report"

    def _get_report_converter(self):
        return f"_render_{self.report_type.replace('-', '_')}"
