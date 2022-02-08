from odoo import fields, models


class ReportDynamicAlias(models.Model):
    _name = "report.dynamic.alias"
    _description = "Replace expressions before rendering"

    expression_from = fields.Char(
        required=True, help="Look for this in report_id.section_ids.content"
    )
    expression_to = fields.Char(
        required=True, help="Replace with this in report_id.section_ids.content"
    )
    is_active = fields.Boolean(
        "Active", default=True, help="To use the record when prerendering"
    )
