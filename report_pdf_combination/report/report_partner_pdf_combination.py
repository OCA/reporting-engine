# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.report_pdf_combination.partner_pdf_combination'
    _inherit = 'report.report_pdf_combination.abstract'

    def get_files_for_pdf_combination_report(self, workbook, data, partners):
        for obj in partners:
            # TODO: implement it to use in unittests
            pass
