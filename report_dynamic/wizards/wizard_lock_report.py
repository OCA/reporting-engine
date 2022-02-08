from odoo import fields, models


class WizardLockReport(models.TransientModel):
    _name = "wizard.lock.report"
    _description = "Provide lock date for report"

    report_id = fields.Many2one("report.dynamic", "Report")
    lock_date = fields.Date(default=fields.Date.today(), required=True)

    def action_lock_report(self):
        """Lock the report on given date"""
        self.ensure_one()
        self.report_id.lock_date = self.lock_date
