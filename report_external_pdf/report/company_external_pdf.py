# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class CompanyExternalPDF(models.AbstractModel):
    _name = "report.report_external_pdf.company_external_pdf"
    _inherit = "report.report_external_pdf.abstract"
    _description = "Demo PDF external generation"

    def _render_report(self, docids, data):
        return self.env.ref("web.action_report_internalpreview").render(
            self.env["res.partner"].browse(docids)
        )[0]
