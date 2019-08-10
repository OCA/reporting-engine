# Copyright 2009-2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


# TODO:
# make PR to move this class as well as the report_xlsx test class
# to the tests folder (requires dynamic update Odoo registry when
# running unit tests.
class TestPartnerXlsx(models.AbstractModel):
    _name = 'report.report_xlsx_helper.test_partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _get_ws_params(self, wb, data, partners):

        partner_template = {
            'name': {
                'header': {
                    'value': 'Name',
                },
                'data': {
                    'value': self._render("partner.name"),
                },
                'width': 20,
            },
            'number_of_contacts': {
                'header': {
                    'value': '# Contacts',
                },
                'data': {
                    'value': self._render("len(partner.child_ids)"),
                },
                'width': 10,
            },
            'is_customer': {
                'header': {
                    'value': 'Customer',
                },
                'data': {
                    'value': self._render("partner.customer"),
                },
                'width': 10,
            },
            'is_customer_formula': {
                'header': {
                    'value': 'Customer Y/N ?',
                },
                'data': {
                    'type': 'formula',
                    'value': self._render("customer_formula"),
                },
                'width': 14,
            },
            'date': {
                'header': {
                    'value': 'Date',
                },
                'data': {
                    'value': self._render("partner.date"),
                },
                'width': 13,
            },
        }

        ws_params = {
            'ws_name': 'Partners',
            'generate_ws_method': '_partner_report',
            'title': 'Partners',
            'wanted_list': [k for k in partner_template],
            'col_specs': partner_template,
        }

        return [ws_params]

    def _partner_report(self, workbook, ws, ws_params, data, partners):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params)
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_yellow_left)
        ws.freeze_panes(row_pos, 0)

        wl = ws_params['wanted_list']

        for partner in partners:
            is_customer_pos = 'is_customer' in wl and \
                wl.index('is_customer')
            is_customer_cell = self._rowcol_to_cell(
                row_pos, is_customer_pos)
            customer_formula = 'IF({},"Y", "N")'.format(is_customer_cell)
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='data',
                render_space={
                    'partner': partner,
                    'customer_formula': customer_formula,
                },
                default_format=self.format_tcell_left)
