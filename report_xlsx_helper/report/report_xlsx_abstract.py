# Copyright 2009-2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, date
import re
from types import CodeType
from xlsxwriter.utility import xl_rowcol_to_cell

from odoo import fields, models, _
from odoo.exceptions import UserError


class ReportXlsxAbstract(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        for ws_params in self._get_ws_params(workbook, data, objects):
            ws_name = ws_params.get('ws_name')
            ws_name = self._check_ws_name(ws_name)
            ws = workbook.add_worksheet(ws_name)
            generate_ws_method = getattr(
                self, ws_params['generate_ws_method'])
            generate_ws_method(workbook, ws, ws_params, data, objects)

    def _check_ws_name(self, name, sanitize=True):
        pattern = re.compile(r'[/\\*\[\]:?]')  # invalid characters: /\*[]:?
        max_chars = 31
        if sanitize:
            # we could drop these two lines since a similar
            # sanitize is done in tools.misc PatchedXlsxWorkbook
            name = pattern.sub('', name)
            name = name[:max_chars]
        else:
            if len(name) > max_chars:
                raise UserError(_(
                    "Programming Error:\n\n"
                    "Excel Sheet name '%s' should not exceed %s characters."
                ) % (name, max_chars))
            special_chars = pattern.findall(name)
            if special_chars:
                raise UserError(_(
                    "Programming Error:\n\n"
                    "Excel Sheet name '%s' contains unsupported special "
                    "characters: '%s'."
                ) % (name, special_chars))
        return name

    def _get_ws_params(self, workbook, data, objects):
        """
        Return list of dictionaries with parameters for the
        worksheets.

        Keywords:
        - 'generate_ws_method': mandatory
        - 'ws_name': name of the worksheet
        - 'title': title of the worksheet
        - 'wanted_list': list of column names
        - 'col_specs': cf. XXX

        The 'generate_ws_method' must be present in your report
        and contain the logic to generate the content of the worksheet.
        """
        return []

    def _define_xls_headers(self, workbook):
        """
        Predefined worksheet headers/footers.
        """
        hf_params = {
            'font_size': 8,
            'font_style': 'I',  # B: Bold, I:  Italic, U: Underline
        }
        self.xls_headers = {
            'standard': ''
        }
        report_date = fields.Datetime.context_timestamp(
            self.env.user, datetime.now()).strftime('%Y-%m-%d %H:%M')
        self.xls_footers = {
            'standard': (
                '&L&%(font_size)s&%(font_style)s' + report_date +
                '&R&%(font_size)s&%(font_style)s&P / &N'
                ) % hf_params,
        }

    def _define_formats(self, workbook):
        """
        This section contains a number of pre-defined formats.
        It is recommended to use these in order to have a
        consistent look & feel between your XLSX reports.
        """
        self._define_xls_headers(workbook)

        border_grey = '#D3D3D3'
        border = {'border': True, 'border_color': border_grey}
        theader = dict(border, bold=True)
        bg_yellow = '#FFFFCC'
        bg_blue = '#CCFFFF'
        num_format = '#,##0.00'
        num_format_conditional = '{0};[Red]-{0};{0}'.format(num_format)
        pct_format = '#,##0.00%'
        pct_format_conditional = '{0};[Red]-{0};{0}'.format(pct_format)
        int_format = '#,##0'
        int_format_conditional = '{0};[Red]-{0};{0}'.format(int_format)
        date_format = 'YYYY-MM-DD'
        theader_yellow = dict(theader, bg_color=bg_yellow)
        theader_blue = dict(theader, bg_color=bg_blue)

        # format for worksheet title
        self.format_ws_title = workbook.add_format(
            {'bold': True, 'font_size': 14})

        # no border formats
        self.format_left = workbook.add_format({'align': 'left'})
        self.format_center = workbook.add_format({'align': 'center'})
        self.format_right = workbook.add_format({'align': 'right'})
        self.format_amount_left = workbook.add_format(
            {'align': 'left', 'num_format': num_format})
        self.format_amount_center = workbook.add_format(
            {'align': 'center', 'num_format': num_format})
        self.format_amount_right = workbook.add_format(
            {'align': 'right', 'num_format': num_format})
        self.format_amount_conditional_left = workbook.add_format(
            {'align': 'left', 'num_format': num_format_conditional})
        self.format_amount_conditional_center = workbook.add_format(
            {'align': 'center', 'num_format': num_format_conditional})
        self.format_amount_conditional_right = workbook.add_format(
            {'align': 'right', 'num_format': num_format_conditional})
        self.format_percent_left = workbook.add_format(
            {'align': 'left', 'num_format': pct_format})
        self.format_percent_center = workbook.add_format(
            {'align': 'center', 'num_format': pct_format})
        self.format_percent_right = workbook.add_format(
            {'align': 'right', 'num_format': pct_format})
        self.format_percent_conditional_left = workbook.add_format(
            {'align': 'left', 'num_format': pct_format_conditional})
        self.format_percent_conditional_center = workbook.add_format(
            {'align': 'center', 'num_format': pct_format_conditional})
        self.format_percent_conditional_right = workbook.add_format(
            {'align': 'right', 'num_format': pct_format_conditional})
        self.format_integer_left = workbook.add_format(
            {'align': 'left', 'num_format': int_format})
        self.format_integer_center = workbook.add_format(
            {'align': 'center', 'num_format': int_format})
        self.format_integer_right = workbook.add_format(
            {'align': 'right', 'num_format': int_format})
        self.format_integer_conditional_left = workbook.add_format(
            {'align': 'right', 'num_format': int_format_conditional})
        self.format_integer_conditional_center = workbook.add_format(
            {'align': 'center', 'num_format': int_format_conditional})
        self.format_integer_conditional_right = workbook.add_format(
            {'align': 'right', 'num_format': int_format_conditional})
        self.format_date_left = workbook.add_format(
            {'align': 'left', 'num_format': date_format})
        self.format_date_center = workbook.add_format(
            {'align': 'center', 'num_format': date_format})
        self.format_date_right = workbook.add_format(
            {'align': 'right', 'num_format': date_format})

        self.format_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True})
        self.format_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True})
        self.format_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True})
        self.format_amount_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True, 'num_format': num_format})
        self.format_amount_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': num_format})
        self.format_amount_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True, 'num_format': num_format})
        self.format_amount_conditional_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True,
             'num_format': num_format_conditional})
        self.format_amount_conditional_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True,
             'num_format': num_format_conditional})
        self.format_amount_conditional_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True,
             'num_format': num_format_conditional})
        self.format_percent_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True, 'num_format': pct_format})
        self.format_percent_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': pct_format})
        self.format_percent_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True, 'num_format': pct_format})
        self.format_percent_conditional_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True,
             'num_format': pct_format_conditional})
        self.format_percent_conditional_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True,
             'num_format': pct_format_conditional})
        self.format_percent_conditional_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True,
             'num_format': pct_format_conditional})
        self.format_integer_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True, 'num_format': int_format})
        self.format_integer_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': int_format})
        self.format_integer_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True, 'num_format': int_format})
        self.format_integer_conditional_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True,
             'num_format': int_format_conditional})
        self.format_integer_conditional_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True,
             'num_format': int_format_conditional})
        self.format_integer_conditional_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True,
             'num_format': int_format_conditional})
        self.format_date_left_bold = workbook.add_format(
            {'align': 'left', 'bold': True, 'num_format': date_format})
        self.format_date_center_bold = workbook.add_format(
            {'align': 'center', 'bold': True, 'num_format': date_format})
        self.format_date_right_bold = workbook.add_format(
            {'align': 'right', 'bold': True, 'num_format': date_format})

        # formats for worksheet table column headers
        self.format_theader_yellow_left = workbook.add_format(theader_yellow)
        self.format_theader_yellow_center = workbook.add_format(
            dict(theader_yellow, align='center'))
        self.format_theader_yellow_right = workbook.add_format(
            dict(theader_yellow, align='right'))
        self.format_theader_yellow_amount_left = workbook.add_format(
            dict(theader_yellow, num_format=num_format, align='left'))
        self.format_theader_yellow_amount_center = workbook.add_format(
            dict(theader_yellow, num_format=num_format, align='center'))
        self.format_theader_yellow_amount_right = workbook.add_format(
            dict(theader_yellow, num_format=num_format, align='right'))

        self.format_theader_yellow_amount_conditional_left = workbook.\
            add_format(dict(theader_yellow, num_format=num_format_conditional,
                       align='left'))
        self.format_theader_yellow_amount_conditional_center = workbook.\
            add_format(dict(theader_yellow, num_format=num_format_conditional,
                            align='center'))
        self.format_theader_yellow_amount_conditional_right = workbook.\
            add_format(dict(theader_yellow, num_format=num_format_conditional,
                            align='right'))
        self.format_theader_yellow_percent_left = workbook.add_format(
            dict(theader_yellow, num_format=pct_format, align='left'))
        self.format_theader_yellow_percent_center = workbook.add_format(
            dict(theader_yellow, num_format=pct_format, align='center'))
        self.format_theader_yellow_percent_right = workbook.add_format(
            dict(theader_yellow, num_format=pct_format, align='right'))
        self.format_theader_yellow_percent_conditional_left = workbook.\
            add_format(dict(theader_yellow, num_format=pct_format_conditional,
                            align='left'))
        self.format_theader_yellow_percent_conditional_center = workbook.\
            add_format(dict(theader_yellow, num_format=pct_format_conditional,
                            align='center'))
        self.format_theader_yellow_percent_conditional_right = workbook.\
            add_format(dict(theader_yellow, num_format=pct_format_conditional,
                            align='right'))
        self.format_theader_yellow_integer_left = workbook.add_format(
            dict(theader_yellow, num_format=int_format, align='left'))
        self.format_theader_yellow_integer_center = workbook.add_format(
            dict(theader_yellow, num_format=int_format, align='center'))
        self.format_theader_yellow_integer_right = workbook.add_format(
            dict(theader_yellow, num_format=int_format, align='right'))
        self.format_theader_yellow_integer_conditional_left = workbook.\
            add_format(dict(theader_yellow, num_format=int_format_conditional,
                            align='left'))
        self.format_theader_yellow_integer_conditional_center = workbook.\
            add_format(dict(theader_yellow, num_format=int_format_conditional,
                            align='center'))
        self.format_theader_yellow_integer_conditional_right = workbook.\
            add_format(dict(theader_yellow, num_format=int_format_conditional,
                            align='right'))

        self.format_theader_blue_left = workbook.add_format(theader_blue)
        self.format_theader_blue_center = workbook.add_format(
            dict(theader_blue, align='center'))
        self.format_theader_blue_right = workbook.add_format(
            dict(theader_blue, align='right'))
        self.format_theader_blue_amount_left = workbook.add_format(
            dict(theader_blue, num_format=num_format, align='left'))
        self.format_theader_blue_amount_center = workbook.add_format(
            dict(theader_blue, num_format=num_format, align='center'))
        self.format_theader_blue_amount_right = workbook.add_format(
            dict(theader_blue, num_format=num_format, align='right'))
        self.format_theader_blue_amount_conditional_left = workbook.\
            add_format(dict(theader_blue, num_format=num_format_conditional,
                            align='left'))
        self.format_theader_blue_amount_conditional_center = workbook.\
            add_format(dict(theader_blue, num_format=num_format_conditional,
                            align='center'))
        self.format_theader_blue_amount_conditional_right = workbook.\
            add_format(dict(theader_blue, num_format=num_format_conditional,
                            align='right'))
        self.format_theader_blue_percent_left = workbook.add_format(
            dict(theader_blue, num_format=pct_format, align='left'))
        self.format_theader_blue_percent_center = workbook.add_format(
            dict(theader_blue, num_format=pct_format, align='center'))
        self.format_theader_blue_percent_right = workbook.add_format(
            dict(theader_blue, num_format=pct_format, align='right'))
        self.format_theader_blue_percent_conditional_left = workbook.\
            add_format(dict(theader_blue, num_format=pct_format_conditional,
                            align='left'))
        self.format_theader_blue_percent_conditional_center = workbook.\
            add_format(dict(theader_blue, num_format=pct_format_conditional,
                            align='center'))
        self.format_theader_blue_percent_conditional_right = workbook.\
            add_format(dict(theader_blue, num_format=pct_format_conditional,
                            align='right'))
        self.format_theader_blue_integer_left = workbook.add_format(
            dict(theader_blue, num_format=int_format, align='left'))
        self.format_theader_blue_integer_center = workbook.add_format(
            dict(theader_blue, num_format=int_format, align='center'))
        self.format_theader_blue_integer_right = workbook.add_format(
            dict(theader_blue, num_format=int_format, align='right'))
        self.format_theader_blue_integer_conditional_left = workbook.\
            add_format(dict(theader_blue, num_format=int_format_conditional,
                            align='left'))
        self.format_theader_blue_integer_conditional_center = workbook.\
            add_format(dict(theader_blue, num_format=int_format_conditional,
                            align='center'))
        self.format_theader_blue_integer_conditional_right = workbook.\
            add_format(dict(theader_blue, num_format=int_format_conditional,
                            align='right'))

        # formats for worksheet table cells
        self.format_tcell_left = workbook.add_format(
            dict(border, align='left'))
        self.format_tcell_center = workbook.add_format(
            dict(border, align='center'))
        self.format_tcell_right = workbook.add_format(
            dict(border, align='right'))
        self.format_tcell_amount_left = workbook.add_format(
            dict(border, num_format=num_format, align='left'))
        self.format_tcell_amount_center = workbook.add_format(
            dict(border, num_format=num_format, align='center'))
        self.format_tcell_amount_right = workbook.add_format(
            dict(border, num_format=num_format, align='right'))
        self.format_tcell_amount_conditional_left = workbook.add_format(
            dict(border, num_format=num_format_conditional, align='left'))
        self.format_tcell_amount_conditional_center = workbook.add_format(
            dict(border, num_format=num_format_conditional, align='center'))
        self.format_tcell_amount_conditional_right = workbook.add_format(
            dict(border, num_format=num_format_conditional, align='right'))
        self.format_tcell_percent_left = workbook.add_format(
            dict(border, num_format=pct_format, align='left'))
        self.format_tcell_percent_center = workbook.add_format(
            dict(border, num_format=pct_format, align='center'))
        self.format_tcell_percent_right = workbook.add_format(
            dict(border, num_format=pct_format, align='right'))
        self.format_tcell_percent_conditional_left = workbook.add_format(
            dict(border, num_format=pct_format_conditional, align='left'))
        self.format_tcell_percent_conditional_center = workbook.add_format(
            dict(border, num_format=pct_format_conditional, align='center'))
        self.format_tcell_percent_conditional_right = workbook.add_format(
            dict(border, num_format=pct_format_conditional, align='right'))
        self.format_tcell_integer_left = workbook.add_format(
            dict(border, num_format=int_format, align='left'))
        self.format_tcell_integer_center = workbook.add_format(
            dict(border, num_format=int_format, align='center'))
        self.format_tcell_integer_right = workbook.add_format(
            dict(border, num_format=int_format, align='right'))
        self.format_tcell_integer_conditional_left = workbook.add_format(
            dict(border, num_format=int_format_conditional, align='left'))
        self.format_tcell_integer_conditional_center = workbook.add_format(
            dict(border, num_format=int_format_conditional, align='center'))
        self.format_tcell_integer_conditional_right = workbook.add_format(
            dict(border, num_format=int_format_conditional, align='right'))
        self.format_tcell_date_left = workbook.add_format(
            dict(border, num_format=date_format, align='left'))
        self.format_tcell_date_center = workbook.add_format(
            dict(border, num_format=date_format, align='center'))
        self.format_tcell_date_right = workbook.add_format(
            dict(border, num_format=date_format, align='right'))

        self.format_tcell_left_bold = workbook.add_format(
            dict(border, align='left', bold=True))
        self.format_tcell_center_bold = workbook.add_format(
            dict(border, align='center', bold=True))
        self.format_tcell_right_bold = workbook.add_format(
            dict(border, align='right', bold=True))
        self.format_tcell_amount_left_bold = workbook.add_format(
            dict(border, num_format=num_format, align='left', bold=True))
        self.format_tcell_amount_center_bold = workbook.add_format(
            dict(border, num_format=num_format, align='center', bold=True))
        self.format_tcell_amount_right_bold = workbook.add_format(
            dict(border, num_format=num_format, align='right', bold=True))
        self.format_tcell_amount_conditional_left_bold = workbook.\
            add_format(dict(border, num_format=num_format_conditional,
                            align='left', bold=True))
        self.format_tcell_amount_conditional_center_bold = workbook.\
            add_format(dict(border, num_format=num_format_conditional,
                            align='center', bold=True))
        self.format_tcell_amount_conditional_right_bold = workbook.\
            add_format(dict(border, num_format=num_format_conditional,
                            align='right', bold=True))
        self.format_tcell_percent_left_bold = workbook.add_format(
            dict(border, num_format=pct_format, align='left', bold=True))
        self.format_tcell_percent_center_bold = workbook.add_format(
            dict(border, num_format=pct_format, align='center', bold=True))
        self.format_tcell_percent_right_bold = workbook.add_format(
            dict(border, num_format=pct_format, align='right', bold=True))
        self.format_tcell_percent_conditional_left_bold = workbook.\
            add_format(dict(border, num_format=pct_format_conditional,
                            align='left', bold=True))
        self.format_tcell_percent_conditional_center_bold = workbook.\
            add_format(dict(border, num_format=pct_format_conditional,
                            align='center', bold=True))
        self.format_tcell_percent_conditional_right_bold = workbook.\
            add_format(dict(border, num_format=pct_format_conditional,
                            align='right', bold=True))
        self.format_tcell_integer_left_bold = workbook.add_format(
            dict(border, num_format=int_format, align='left', bold=True))
        self.format_tcell_integer_center_bold = workbook.add_format(
            dict(border, num_format=int_format, align='center', bold=True))
        self.format_tcell_integer_right_bold = workbook.add_format(
            dict(border, num_format=int_format, align='right', bold=True))
        self.format_tcell_integer_conditional_left_bold = workbook.\
            add_format(dict(border, num_format=int_format_conditional,
                            align='left', bold=True))
        self.format_tcell_integer_conditional_center_bold = workbook.\
            add_format(dict(border, num_format=int_format_conditional,
                            align='center', bold=True))
        self.format_tcell_integer_conditional_right_bold = workbook.\
            add_format(dict(border, num_format=int_format_conditional,
                            align='right', bold=True))
        self.format_tcell_date_left_bold = workbook.add_format(
            dict(border, num_format=date_format, align='left', bold=True))
        self.format_tcell_date_center_bold = workbook.add_format(
            dict(border, num_format=date_format, align='center', bold=True))
        self.format_tcell_date_right_bold = workbook.add_format(
            dict(border, num_format=date_format, align='right', bold=True))

    def _set_column_width(self, ws, ws_params):
        """
        Set width for all columns included in the 'wanted_list'.
        """
        col_specs = ws_params.get('col_specs')
        wl = ws_params.get('wanted_list') or []
        for pos, col in enumerate(wl):
            if col not in col_specs:
                raise UserError(_(
                    "Programming Error:\n\n"
                    "The '%s' column is not defined in the worksheet "
                    "column specifications.") % col)
            ws.set_column(pos, pos, col_specs[col]['width'])

    def _write_ws_title(self, ws, row_pos, ws_params, merge_range=False):
        """
        Helper function to ensure consistent title formats
        troughout all worksheets.
        Requires 'title' keyword in ws_params.
        """
        title = ws_params.get('title')
        if not title:
            raise UserError(_(
                "Programming Error:\n\n"
                "The 'title' parameter is mandatory "
                "when calling the '_write_ws_title' method."))
        if merge_range:
            wl = ws_params.get('wanted_list')
            if wl and len(wl) > 1:
                ws.merge_range(
                    row_pos, 0, row_pos, len(wl) - 1,
                    title, self.format_ws_title)
        else:
            ws.write_string(row_pos, 0, title, self.format_ws_title)
        return row_pos + 2

    def _write_line(self, ws, row_pos, ws_params, col_specs_section=None,
                    render_space=None, default_format=None,
                    col_specs='col_specs', wanted_list='wanted_list'):
        """
        Write a line with all columns included in the 'wanted_list'.
        Use the entry defined by the col_specs_section.
        An empty cell will be written if no col_specs_section entry
        for a column.
        """
        col_specs = ws_params.get(col_specs)
        wl = ws_params.get(wanted_list) or []
        pos = 0
        for col in wl:
            if col not in col_specs:
                raise UserError(_(
                    "Programming Error:\n\n"
                    "The '%s' column is not defined the worksheet "
                    "column specifications.") % col)
            colspan = col_specs[col].get('colspan') or 1
            cell_spec = col_specs[col].get(col_specs_section) or {}
            if not cell_spec:
                cell_value = None
                cell_type = 'blank'
                cell_format = default_format
            else:
                cell_value = cell_spec.get('value')
                if isinstance(cell_value, CodeType):
                    cell_value = self._eval(cell_value, render_space)
                cell_type = cell_spec.get('type')
                cell_format = cell_spec.get('format') or default_format
                if not cell_type:
                    # test bool first since isinstance(val, int) returns
                    # True when type(val) is bool
                    if isinstance(cell_value, bool):
                        cell_type = 'boolean'
                    elif isinstance(cell_value, str):
                        cell_type = 'string'
                    elif isinstance(cell_value, (int, float)):
                        cell_type = 'number'
                    elif isinstance(cell_value, datetime):
                        cell_type = 'datetime'
                    elif isinstance(cell_value, date):
                        cell_value = datetime.combine(
                            cell_value, datetime.min.time())
                        cell_type = 'datetime'
                    else:
                        if not cell_value:
                            cell_type = 'blank'
                        else:
                            msg = _(
                                "%s, _write_line : programming error "
                                "detected while processing "
                                "col_specs_section %s, column %s"
                            ) % (__name__, col_specs_section, col)
                            if cell_value:
                                msg += _(", cellvalue %s") % cell_value
                            raise UserError(msg)
            colspan = cell_spec.get('colspan') or colspan
            args_pos = [row_pos, pos]
            args_data = [cell_value]
            if cell_format:
                if isinstance(cell_format, CodeType):
                    cell_format = self._eval(cell_format, render_space)
                args_data.append(cell_format)
            if colspan > 1:
                args_pos += [row_pos, pos + colspan - 1]
                args = args_pos + args_data
                ws.merge_range(*args)
            else:
                ws_method = getattr(ws, 'write_%s' % cell_type)
                args = args_pos + args_data
                ws_method(*args)
            pos += colspan

        return row_pos + 1

    @staticmethod
    def _render(code):
        return compile(code, '<string>', 'eval')

    @staticmethod
    def _eval(val, render_space):
        if not render_space:
            render_space = {}
        if 'datetime' not in render_space:
            render_space['datetime'] = datetime
        # the use of eval is not a security thread as long as the
        # col_specs template is defined in a python module
        return eval(val, render_space)  # pylint: disable=W0123,W8112

    @staticmethod
    def _rowcol_to_cell(row, col, row_abs=False, col_abs=False):
        return xl_rowcol_to_cell(row, col, row_abs=row_abs, col_abs=col_abs)
