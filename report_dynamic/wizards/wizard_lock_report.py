# Copyright 2022 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizardLockReport(models.TransientModel):
    """Lock report at given date, make it readonly"""

    _name = "wizard.lock.report"
    _description = "Provide lock date for report"

    report_id = fields.Many2one(comodel_name="report.dynamic", string="Report")
    lock_date = fields.Date(default=fields.Date.today(), required=True)

    def action_lock_report(self):
        """Lock the report on given date"""
        self.ensure_one()
        self.report_id.lock_date = self.lock_date
