# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import xlwt
import lxml.html
import logging
import base64
import datetime
from tempfile import mkstemp
from cStringIO import StringIO
from openerp import models, api, _
from openerp.exceptions import Warning

_logger = logging.getLogger('report_xls_template')


class Report(models.Model):

    _inherit = 'report'

    @api.v7
    def get_html(self, cr, uid, ids, report_name, data=None, context=None):
        report = self._get_xls_report_from_name(cr, uid, report_name)
        if report:
            try:
                report_model_name = 'report.%s' % report_name
                particularreport_obj = self.pool[report_model_name]
                return particularreport_obj.render_html(
                    cr, uid, ids, data=data, context=context)
            except KeyError:
                report_obj = self.pool[report.model]
                docs = report_obj.browse(cr, uid, ids, context=context)
                docargs = {
                           'doc_ids': ids,
                           'doc_model': report.model,
                           'docs': docs,
                           }
                return self.pool.get('report').render(
                    cr, uid, [], report.report_name, docargs, context=context)
        else:
            return super(Report, self).get_html(
                cr, uid, ids, report_name, data=data, context=context)

    @api.v7
    def get_xls(self, cr, uid, ids, report_name,
                html=None, data=None, context=None):
        """
        This method generates and returns xls version of a report.
        """
        if context is None:
            context = {}

        report_obj = self.pool.get('report')
        if html is None:
            html = report_obj.get_html(
                cr, uid, ids, report_name, data=data, context=context)

        # Ensure the current document is utf-8 encoded.
        html = html.decode('utf-8')

        def datetime_from_str(dt_str):
            formats = [
                # <scope>, <pattern>, <format>
                ('day', 'YYYY-MM-DD', '%Y-%m-%d'),
                ('second', 'YYYY-MM-DD HH:MM:SS', '%Y-%m-%d %H:%M:%S'),
                ('microsecond', 'YYYY-MM-DD HH:MM:SS', '%Y-%m-%d %H:%M:%S'),
            ]
            for scope, pattern, format in formats:
                if scope == 'microsecond':
                    if dt_str.count('.') != 1:
                        continue
                    dt_str, microseconds_str = dt_str.split('.')
                    try:
                        microsecond = int((microseconds_str + '000000')[:6])
                    except ValueError:
                        continue
                try:
                    t = datetime.datetime.strptime(dt_str, format)
                except ValueError:
                    pass
                else:
                    if scope == 'microsecond':
                        t = t.replace(microsecond=microsecond)
                    return t
            else:
                raise ValueError

        # Method should be rewriten for a more complex rendering
        def render_element_content(element):
            res = ''
            if isinstance(element.text, (str, unicode)):
                if element.tag == 'pre':
                    res += element.text
                else:
                    res += element.text.strip()
            for child in element:
                res += render_element_content(child)
            if isinstance(element.tail, (str, unicode)):
                res += element.tail.strip()
            return res

        # Method identify the data type
        def render_element_type(value):
            dt = ''
            try:
                dt = datetime_from_str(value)
                if dt or dt is not None:
                    return dt
            except:
                try:
                    return float(value)
                except:  # Not Float Type
                    return value

        def insert_bitmap(worksheet, image, row_index, column_index):
            src = image.get('src', False)
            scale_x = float(image.get('scale_x', False)) or 1
            scale_y = float(image.get('scale_y', False)) or 1
            offset_x = float(image.get('offset_x', False)) or 1
            offset_y = float(image.get('offset_y', False)) or 1
            if not src:
                return
            src = src.replace('data:image/bmp;base64,', '')
            image_fd, image_path = mkstemp(suffix='.bmp', prefix='report.tmp.')
            tmp_file = open(image_path, 'wb')
            tmp_file.write(base64.decodestring(src))
            tmp_file.close()
            os.close(image_fd)
            worksheet.insert_bitmap(
                image_path, row_index, column_index, x=offset_x, y=offset_y,
                scale_x=scale_x, scale_y=scale_y)
            os.remove(image_path)

        def write_column(
                worksheet, column, row_index,
                column_index, rowspan_number, colspan_number):
            style = None
            colwidth = column.get('colwidth', False)
            formula = bool(column.get('formula', False))
            try:
                style_str = column.get('easyfx', False)
                format_str = column.get('num_format_str', False)
                if style_str and format_str:
                    style = xlwt.easyxf(style_str, num_format_str=format_str)
                elif style_str and not format_str:
                    style = xlwt.easyxf(style_str, None)
                elif format_str and not style_str:
                    style = xlwt.easyxf('', num_format_str=format_str)
            except:
                _logger.info('An error ocurred while loading the style')
            if colspan_number or rowspan_number:
                try:
                    colspan_number = colspan_number and \
                        (colspan_number - 1) or 0
                    rowspan_number = rowspan_number and \
                        (rowspan_number - 1) or 0
                    if style:
                        if formula:
                            try:
                                worksheet.write_merge(
                                    row_index, row_index + rowspan_number,
                                    column_index, column_index +
                                    colspan_number, xlwt.Formula(column.text),
                                    style)
                            except:
                                _logger.info(
                                    'An error ocurred writing the formula.')
                        else:
                            worksheet.write_merge(
                                row_index, row_index + rowspan_number,
                                column_index, column_index + colspan_number,
                                render_element_type(
                                    render_element_content(column)
                                ), style)
                    else:
                        # Use default style
                        if formula:
                            try:
                                worksheet.write_merge(
                                    row_index, row_index + rowspan_number,
                                    column_index, column_index +
                                    colspan_number, xlwt.Formula(column.text))
                            except:
                                _logger.info(
                                    'An error ocurred writing the formula.')
                        else:
                            worksheet.write_merge(
                                row_index, row_index + rowspan_number,
                                column_index, column_index + colspan_number,
                                render_element_type(
                                    render_element_content(column)))
                    # Review column width
                    if colwidth:
                        factor = 1
                        if colspan_number:
                            factor += colspan_number
                        colwidth = int(colwidth) // factor
                        for i in range(column_index, column_index + factor):
                            try:
                                worksheet.col(i).width = int(colwidth) * 256
                            except:
                                _logger.info(
                                    'An error ocurred setting the '
                                    'column width.')
                except:
                    _logger.info(
                        'An error ocurred while merging cells')
            else:
                if style:
                    if formula:
                        try:
                            worksheet.write(
                                row_index, column_index,
                                xlwt.Formula(column.text), style)
                        except:
                            _logger.info(
                                'An error ocurred writing the formula.')
                    else:
                        worksheet.write(
                            row_index, column_index, render_element_type(
                                render_element_content(column)),
                            style)
                else:
                    # Use default style
                    if formula:
                        try:
                            worksheet.write(
                                row_index, column_index,
                                xlwt.Formula(column.text))
                        except:
                            _logger.info(
                                'An error ocurred writing the formula.')
                    else:
                        worksheet.write(
                            row_index, column_index, render_element_type(
                                render_element_content(column)))
                # Review column width
                if colwidth:
                    try:
                        worksheet.col(column_index).width = int(colwidth) * 256
                    except:
                        _logger.info(
                            'An error ocurred setting the '
                            'column width.')
            try:
                # Insert all bitmaps
                for image in column.xpath('img'):
                    insert_bitmap(worksheet, image, row_index, column_index)
            except:
                _logger.info('An error ocurred inserting images.')

        # Create the workbook
        workbook = xlwt.Workbook()
        try:
            root = lxml.html.fromstring(html)
            # find the workbook div element
            div_workbook = root.xpath("//div[@class='workbook']")[0]
            # Find every worksheet on the report
            worksheet_counter = 1
            for div_worksheet in div_workbook.xpath(
                    "//div[@class='worksheet']"):
                # Add a worksheet with the desired name
                try:
                    if not xlwt.Utils.valid_sheet_name(div_worksheet.get(
                            'name', _('Data') + str(worksheet_counter))):
                        raise Warning(_('Invalid worksheet name.'))
                    worksheet = workbook.add_sheet(div_worksheet.get(
                            'name', _('Data') + str(worksheet_counter)))
                except (Warning, Exception) as exc:
                    raise Warning(exc.message)
                # Set number of pages
                fixpages = div_worksheet.get('fixpages', False)
                wpages = div_worksheet.get('wpages', False)
                hpages = div_worksheet.get('hpages', False)
                if fixpages:
                    worksheet.set_fit_num_pages(int(fixpages))
                if wpages:
                    worksheet.set_fit_width_to_pages(int(wpages))
                if hpages:
                    worksheet.set_fit_height_to_pages(int(hpages))
                # Find all tables to add tho the worksheet
                row_index = 0
                for table in div_worksheet.xpath("table"):
                    # Write all headers to the worksheet
                    for header_row in table.xpath("thead/tr"):
                        column_index = 0
                        merged_rows = []
                        rowheight = header_row.get('rowheight', False)
                        for column in header_row.xpath('th'):
                            colspan_number = int(column.get('colspan', False))
                            rowspan_number = int(column.get('rowspan', False))
                            write_column(
                                worksheet, column, row_index,
                                column_index, rowspan_number, colspan_number)
                            if colspan_number:
                                column_index += (colspan_number - 1)
                            if rowspan_number:
                                merged_rows.append(rowspan_number)
                            column_index += 1
                        if rowheight:
                            worksheet.row(
                                row_index).height = int(rowheight) * 256
                            fnt = xlwt.Font()
                            fnt.height = int(rowheight) * 256
                            style = xlwt.XFStyle()
                            style.font = fnt
                            worksheet.row(row_index).set_style(style)
                        row_index += merged_rows and max(merged_rows) or 1
                    # Write all content to the worksheet
                    for content_row in table.xpath("tbody/tr"):
                        column_index = 0
                        merged_rows = []
                        rowheight = content_row.get('rowheight', False)
                        for column in content_row.xpath('td'):
                            colspan_number = int(column.get('colspan', False))
                            rowspan_number = int(column.get('rowspan', False))
                            write_column(
                                worksheet, column, row_index,
                                column_index, rowspan_number, colspan_number)
                            if colspan_number:
                                column_index += (colspan_number - 1)
                            if rowspan_number:
                                merged_rows.append(rowspan_number)
                            column_index += 1
                        if rowheight:
                            worksheet.row(
                                row_index).height = int(rowheight) * 256
                            fnt = xlwt.Font()
                            fnt.height = int(rowheight) * 256
                            style = xlwt.XFStyle()
                            style.font = fnt
                            worksheet.row(row_index).set_style(style)
                        row_index += merged_rows and max(merged_rows) or 1
                worksheet_counter += 1
        except:
            raise Warning(
                _('An error occurred while parsing the view into file.'))

        output = StringIO()
        workbook.save(output)  # Save the workbook that we are going to return
        output.seek(0)
        return output.read()

    @api.v8
    def get_xls(self, records, report_name, html=None, data=None):
        return self._model.get_xls(
            self._cr, self._uid, records.ids, report_name,
            html=html, data=data, context=self._context)

    @api.v7
    def get_ods(
            self, cr, uid, ids, report_name,
            html=None, data=None, context=None):
        raise NotImplementedError

    @api.v8
    def get_ods(self, records, report_name, html=None, data=None):
        raise NotImplementedError

    def _get_xls_report_from_name(self, cr, uid, report_name):
        """
        Get the first record of ir.actions.report.xml having
        the ``report_name`` as value for the field report_name.
        """
        report_obj = self.pool['ir.actions.report.xml']
        qweb_xls_types = ['qweb-xls', 'qweb-ods']
        conditions = [
            ('report_type', 'in', qweb_xls_types),
            ('report_name', '=', report_name)]
        idreport = report_obj.search(cr, uid, conditions)
        if idreport:
            return report_obj.browse(cr, uid, idreport[0])
        return None
