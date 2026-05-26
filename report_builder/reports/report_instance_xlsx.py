# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import numbers
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)


class ReportBuilderReportInstanceXlsx(models.AbstractModel):
    _name = "report.report_builder.report_instance_xlsx"
    _description = "XLSX report for Report Builder instances"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        # get the computed result of the report
        columns_data = objects._get_data()
        values = objects.process_information(data.get("pivot_date"), data.get("domain"))
        row_id = 0
        sheet = workbook.add_worksheet(objects[0].name[:31])
        column_id = 0
        for column in columns_data["columns"]:
            column_id += 1
            sheet.write(row_id, column_id, column["name"])
        for row in columns_data["rows"]:
            row_id += 1
            column_id = 0
            style_props = row.get("parameters") or {}
            row_xlsx_style = self.env["report.style"]._get_style_xlsx(
                "string", style_props
            )
            row_format = workbook.add_format(row_xlsx_style)
            sheet.write(row_id, column_id, row["name"], row_format)
            for column in columns_data["columns"]:
                column_id += 1
                value = values.get(row["id"], {}).get(column["id"], {}).get("total")
                if isinstance(value, numbers.Number):
                    value = float(value)
                elif isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    value = str(value) if value is not None else ""
                row_xlsx_style = self.env["report.style"]._get_style_xlsx(
                    "number", style_props
                )
                row_format = workbook.add_format(row_xlsx_style)
                sheet.write(row_id, column_id, value, row_format)
