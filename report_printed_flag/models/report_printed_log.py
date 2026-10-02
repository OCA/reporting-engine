from odoo import fields, models


class ReportPrintedLog(models.Model):
    """
    Log model to track report printing events.
    Each record represents a single execution of a report on a specific
    business document.
    This model is used to:
    - Audit report usage
    - Track which reports were printed per record
    - Support computed fields such as printed report names
    The log is created automatically when a report is generated and the
    corresponding configuration enables logging.
    """

    _name = "report.printed.log"
    _description = "Report Printed Log"
    _order = "create_date desc"

    res_model = fields.Char(required=True, index=True)
    res_id = fields.Many2oneReference(
        string="Related Record",
        model_field="res_model",
        index=True,
        required=True,
    )
    report_id = fields.Many2one(
        "ir.actions.report",
        required=True,
        ondelete="cascade",
    )
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
    )
    name = fields.Char(required=True)
