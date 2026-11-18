# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import csv

from odoo import models


class PartnerCSV(models.AbstractModel):
    _name = "report.report_csv.partner_csv"
    _inherit = "report.report_csv.abstract"
    _description = "Report Partner to CSV"

    def generate_csv_report(self, writer, data, partners):
        writer.writeheader()
        for obj in partners:
            writer.writerow({"name": obj.name, "email": obj.email})

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"].append("name")
        res["fieldnames"].append("email")
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_ALL
        return res
