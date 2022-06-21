# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError


class ReportExternalPDFAbstract(models.AbstractModel):
    _name = "report.report_external_pdf.abstract"
    _description = "report.report_external_pdf.abstract"

    def render_report(self, docids, data):
        return self._render_report(docids, data), "pdf"

    def _render_report(self, docids, data):
        raise ValidationError(_("Function is not defined"))
