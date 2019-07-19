# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from functools import reduce

from xlsxwriter.utility import xl_rowcol_to_cell
from odoo import api, fields, models, _


class ReportSaleOrderXlsx(models.AbstractModel):
    _name = 'report.arch_construction.report_sale_order_xlsx'
    _inherit = 'report.arch_construction.base_xlsx_report'

    def set_cells_size(self, sheet):
        sheet.set_row(0, 30)
        # sheet.set_column(0, 0, 10, self.normal_font)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 35)
        # sheet.set_column(4, 4, 15)
        # sheet.set_column(5, 6, 20)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 20)
        # sheet.set_zoom(100)

    def generate_main_content(self):
        columns = [
            {'key': 'sequence', 'label': _('No.'), 'merge_same_do': True,
             'cell_format': self.normal_font_border_center},
            {'key': 'product_name', 'label': _('Product'),
             'merge_same_do': True
             },
            {'key': 'description', 'label': _('Description'),
             'merge_same_so': True
             },
            {'key': 'length', 'label': _('Length'),
             'cell_format': self.normal_font_border_center},
            {'key': 'width', 'label': _('Width'),
             'merge_same_so': True,
             'cell_format': self.normal_font_border_center,
             },
            {'key': 'height', 'label': _('Height'),
             'cell_format': self.normal_font_border_center,
             'merge_same_so': True
             },
            {'key': 'quantity', 'label': _('Quantity'),
             'merge_same_so': True,
             'cell_format': self.normal_font_border_center,
             },
            {'key': 'uom', 'label': _('UoM'),
             'merge_same_so': True,
             'cell_format': self.normal_font_border_center,
             },
            {'key': 'price_unit',
             'label': _('Unit Price'),
             'cell_format': self.normal_number_border_all,
             'merge_same_so': True
             },
            {'key': 'price_subtotal',
             'label': _('Subtotal'),
             'cell_format': self.normal_number_border_all,
             'merge_same_do': True
             },
            {'key': 'note', 'label': 'Note (Ghi chú)', 'merge_same_do': True},
        ]

        for index, obj in enumerate(self.objects):
            sheet = self.sheets[index]
            report_data = self.get_report_data(sheet, obj)
            self.row_pos = 0

            header_data = report_data.get('header', {})
            lines_data = report_data.get('lines', [])
            self.generate_header(sheet, header_data, columns)

            self.generate_table(sheet, lines_data, columns)

    def get_report_data(self, sheet, obj):
        result = dict()
        result['header'] = self.get_report_header_data(obj)
        result['lines'] = self.get_report_lines(obj)
        return result

    def get_report_lines(self, obj):
        lines = []
        sequence = 1
        for line in obj.order_line:
            line_values = {
                'sequence': sequence,
                'product_name': line.product_id.name,
                'description': line.name,
                'length': line.d_length,
                'width': line.d_width,
                'height': line.d_height,
                'quantity': line.product_uom_qty,
                'uom': line.product_uom.name,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal
            }
            lines.append(line_values)
            sequence += 1

        return lines

    def get_report_header_data(self, obj):
        company_info = self.get_company_info()
        user_name = False
        customer_name = obj.partner_id.name
        customer_address = False
        customer_phone = False
        customer_email = False
        report_title = _('Quotation')
        order_date = False
        return dict(
            **company_info,
            customer_name=customer_name,
            customer_address=customer_address,
            customer_phone=customer_phone,
            customer_email=customer_email,
            user_name=user_name,
            report_title=report_title,
            order_date=order_date
        )

    def generate_header(self, sheet, data, columns):
        # LOGO
        row_pos = self.row_pos
        col_pos = 0
        cell_format = self.normal_bold_font
        header_font = self.header_font
        header_center_font = self.header_center_font
        company_logo = data.get('company_logo', False)
        if company_logo:
            sheet.merge_range(
                row_pos, col_pos,
                row_pos + 2, col_pos + 1,
                '', cell_format
            )
            sheet.insert_image(
                row_pos,
                col_pos,
                'logo.png',
                {
                    'image_data': company_logo,
                    'x_scale': 0.83,
                    'y_scale': 1,
                    # 'x_offset': 5,
                    'y_offset': 10
                }
            )
            col_pos += 2
        # Company name
        company_name = data.get('company_name', '')
        len_columns = len(columns) - 1
        sheet.merge_range(
            row_pos, col_pos,
            row_pos, len_columns,
            company_name.upper(), header_font
        )
        row_pos += 1

        # Company address
        cell_format = self.normal_font
        company_address = data.get('company_address', {})
        sheet.merge_range(
            row_pos, col_pos,
            row_pos, len_columns,
            company_address.get('name_address', '') + ': ' +
            company_address.get('company_address', ''), cell_format
        )
        row_pos += 1

        # Company phone
        company_phone = data.get('company_phone', {})
        sheet.merge_range(
            row_pos, col_pos,
            row_pos, col_pos + 2,
            company_phone.get('name_phone', '') + ': ' +
            company_phone.get('company_phone', ''),
            cell_format
        )
        # Company email
        company_email = data.get('company_email', {})
        sheet.merge_range(
            row_pos, col_pos + 3,
            row_pos, len_columns,
            company_email.get('name_email', '') + ': ' +
            company_email.get('company_email', ''),
            cell_format
        )
        row_pos += 1

        # Company phone
        company_tax = data.get('company_tax', {})
        sheet.merge_range(
            row_pos, col_pos,
            row_pos, col_pos + 2,
            company_tax.get('name_tax', '') + ': ' +
            company_tax.get('company_tax', ''),
            cell_format
        )
        # Company website
        company_website = data.get('company_website', {})
        sheet.merge_range(
            row_pos, col_pos + 3,
            row_pos, len_columns,
            company_website.get('name_website', '') + ': ' +
            company_website.get('company_website', ''),
            cell_format
        )
        row_pos += 1

        # Report title
        row_pos += 1
        report_title = data.get('report_title', '')
        num_of_cols_to_merge = 12
        from_col_pos = col_pos
        to_col_pos = from_col_pos + num_of_cols_to_merge - 1
        sheet.set_row(row_pos, 30)
        sheet.merge_range(
            row_pos, 0, row_pos, len_columns,
            report_title.upper(),
            header_center_font
        )
        row_pos += 1

        # Customer
        customer_col_pos = 0
        customer_name = data.get('customer_name', '')
        sheet.write(
            row_pos, customer_col_pos + 1,
            _('Dear:'),
            self.normal_bold_font
        )
        customer_name = data.get('customer_name', '')
        sheet.merge_range(
            row_pos, customer_col_pos + 2, row_pos, len_columns,
            customer_name,
            cell_format
        )
        row_pos += 1

        # Date range
        preface = (u'Dựa vào nhu cầu của quý khách %s xin trân trọng '
                   u'báo giá các sản phẩm như sau:' % company_name)

        sheet.merge_range(
            row_pos, customer_col_pos, row_pos, len_columns,
            preface,
            cell_format
        )
        row_pos += 1

        self.row_pos = row_pos

        return True

    def generate_table(self, sheet, lines_data, columns):
        self.generate_table_header(sheet, columns)
        self.generate_table_lines(sheet, lines_data, columns)

    def generate_table_header(self, sheet, columns):
        row_pos = self.row_pos

        row_pos += 1
        sheet.set_row(row_pos, 30)
        cell_format = self.table_cell_header
        for col_pos, column in enumerate(columns):
            column_header = column.get('label', '')
            sheet.write(row_pos, col_pos, column_header, cell_format)

        self.row_pos = row_pos

    def generate_table_lines(self, sheet, lines_data, columns):
        row_pos = self.row_pos
        row_pos += 1

        merge_cell_values = []
        stop_row_pos = row_pos
        for line_data in lines_data:
            for col_pos, column in enumerate(columns):
                cell_format = column.get(
                    'cell_format', self.table_cell_border_all
                )
                key = column['key']
                value = line_data.get(key)
                sheet.set_row(row_pos, 60)
                sheet.write(row_pos, col_pos, value, cell_format)

                merge_same_do = column.get('merge_same_do', False)
                first_do = line_data.get('first_do', False)

                # Tracking cell to merge when having same DO first
                if merge_same_do and first_do:
                    merge_cell_values.append(
                        {
                            'key': key,
                            'cell_row_pos': row_pos,
                            'cell_col_pos': col_pos,
                            'value': value,
                            'cell_format': cell_format,
                        }
                    )

                merge_same_so = column.get('merge_same_so', False)
                first_so = line_data.get('first_so', False)

                # Tracking cell to merge when having same SO
                if merge_same_so and first_so:
                    merge_cell_values.append(
                        {
                            'key': key,
                            'cell_row_pos': row_pos,
                            'cell_col_pos': col_pos,
                            'value': value,
                            'cell_format': cell_format,
                        }
                    )
            stop_row_pos = row_pos
            row_pos += 1

        # Group merge cells by column key
        grouped_merge_cells = reduce(
            lambda prev, cell_values: {
                **prev,
                cell_values['key']: prev.get(
                    cell_values['key'], []) + [cell_values]
            }, merge_cell_values, {}
        )

        # Merge cells column by column
        for to_merge_cell_values in grouped_merge_cells.values():
            to_merge_cells = len(to_merge_cell_values)
            for index in range(0, to_merge_cells):
                merge_cell = to_merge_cell_values[index]
                cell_row_pos = merge_cell['cell_row_pos']
                cell_col_pos = merge_cell['cell_col_pos']
                cell_value = merge_cell['value']
                cell_format = merge_cell['cell_format']

                # Get stop_cell_row pos = next cell_row_pos
                if index < to_merge_cells - 1:
                    stop_cell_row_pos = \
                        to_merge_cell_values[index + 1]['cell_row_pos'] - 1

                # stop_cell_row = stop_row_pos if this is the last item
                else:
                    stop_cell_row_pos = stop_row_pos

                if stop_cell_row_pos > cell_row_pos:
                    sheet.merge_range(
                        cell_row_pos, cell_col_pos,
                        stop_cell_row_pos, cell_col_pos,
                        cell_value, cell_format
                    )

        self.row_pos = row_pos

    def _define_formats(self, default_font_size=12):
        super(ReportSaleOrderXlsx, self)._define_formats(
            default_font_size=default_font_size
        )
        normal_font = {
            'font_name': 'Times New Roman',
            'font_size': default_font_size,
            'text_wrap': True,
            'align': 'vcenter'
        }
        format_number = {
            'num_format': '#,###'
        }

        format_report_title = normal_font.copy()
        format_report_title.update({
            'bold': True,
            'font_size': 14,
        })
        self.format_report_title = self.wb.add_format(format_report_title)

        table_cell_border_all = normal_font.copy()
        table_cell_border_all.update({
            'border': 1,
            'valign': 'vcenter',
        })
        self.table_cell_border_all = self.wb.add_format(table_cell_border_all)

        table_cell_header = table_cell_border_all.copy()
        table_cell_header.update({
            'align': 'center',
            'bold': True,
        })
        self.table_cell_header = self.wb.add_format(table_cell_header)

        table_cell_header_align_right = table_cell_header.copy()
        table_cell_header_align_right.update({
            'align': 'right'
        })
        self.table_cell_header_align_right = self.wb.add_format(
            table_cell_header_align_right
        )

        table_cell_number = table_cell_border_all.copy()
        table_cell_number.update({**format_number, 'align': 'right'})
        self.table_cell_number = self.wb.add_format(table_cell_number)

        table_cell_number_bold = table_cell_number.copy()
        table_cell_number_bold.update({'bold': True})
        self.table_cell_number_bold = self.wb.add_format(
            table_cell_number_bold)
