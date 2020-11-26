# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)


class PartnerExportXlsx(models.AbstractModel):
    _name = "report.report_xlsx_helper_demo.partner_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"

    def _get_ws_params(self, wb, data, partners):

        partner_template = {
            "name": {
                "header": {
                    "value": "Name",
                },
                "data": {
                    "value": self._render("partner.name"),
                },
                "width": 20,
            },
            "number_of_contacts": {
                "header": {
                    "value": "# Contacts",
                },
                "data": {
                    "value": self._render("len(partner.child_ids)"),
                },
                "width": 10,
            },
            "is_company": {
                "header": {
                    "value": "Company",
                },
                "data": {
                    "value": self._render("partner.is_company"),
                },
                "width": 10,
            },
            "is_company_formula": {
                "header": {
                    "value": "Company Y/N ?",
                },
                "data": {
                    "type": "formula",
                    "value": self._render("company_formula"),
                },
                "width": 14,
            },
        }

        wanted_list = ["name", "number_of_contacts", "is_company", "is_company_formula"]
        ws_params = {
            "ws_name": "Partners",
            "generate_ws_method": "_partner_report",
            "title": "Partners",
            "wanted_list": wanted_list,
            "col_specs": partner_template,
        }

        return [ws_params]

    def _partner_report(self, workbook, ws, ws_params, data, partners):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        if len(partners) == 1:
            ws_params["title"] = partners.name
        row_pos = self._write_ws_title(ws, row_pos, ws_params)
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_yellow_left"],
        )
        ws.freeze_panes(row_pos, 0)

        wl = ws_params["wanted_list"]

        for partner in partners:
            is_company_pos = "is_company" in wl and wl.index("is_company")
            is_company_cell = self._rowcol_to_cell(row_pos, is_company_pos)
            company_formula = 'IF({},"Y", "N")'.format(is_company_cell)
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                render_space={
                    "partner": partner,
                    "company_formula": company_formula,
                },
                default_format=FORMATS["format_tcell_left"],
            )
