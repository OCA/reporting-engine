# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class PartnerCSV(models.AbstractModel):
    _name = 'report.report_csv.partner_csv'
    _inherit = 'report.report_csv.abstract'

    def generate_csv_report(self, writer, data, partners):
        for obj in partners:
            writer.writeheader()
            writer.writerow({
                'name': obj.name
            })

    def csv_report_options(self):
        res = super().csv_report_options()
        res['fieldnames'].append('name')
        return res
