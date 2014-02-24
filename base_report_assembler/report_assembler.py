# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
import time
import base64
from PyPDF2 import PdfFileReader, PdfFileWriter
from StringIO import StringIO

from openerp.netsvc import ExportService
from openerp.report import report_sxw
from openerp import pooler

_POLLING_DELAY = 0.25


def assemble_pdf(pdf_list):
    """
    Assemble a list of pdf
    """
    # Even though we are using PyPDF2 we can't use PdfFileMerger
    # as this issue still exists in mostly used wktohtml reports version
    # http://code.google.com/p/wkhtmltopdf/issues/detail?id=635
    #merger = PdfFileMerger()
    #merger.append(fileobj=StringIO(invoice_pdf))
    #merger.append(fileobj=StringIO(bvr_pdf))

    #with tempfile.TemporaryFile() as merged_pdf:
        #merger.write(merged_pdf)
        #return merged_pdf.read(), 'pdf'

    output = PdfFileWriter()
    for pdf in pdf_list:
        reader = PdfFileReader(StringIO(pdf))
        for page in range(reader.getNumPages()):
            output.addPage(reader.getPage(page))
    s = StringIO()
    output.write(s)
    return s.getvalue()


class PDFReportAssembler(report_sxw.report_sxw):
    """ PDFReportAssembler allows to put 2 pdf reports in one single pdf"""

    def _generate_all_pdf(self, cr, uid, ids, data, report_ids, context=None):
        """
        Return a list of pdf encoded in base64
        """
        pool = pooler.get_pool(cr.dbname)
        report_obj = pool.get('ir.actions.report.xml')

        spool = ExportService._services['report']

        pdf_reports = []
        report_list = report_obj.browse(cr, uid, report_ids, context=context)
        for report in report_list:

            report_key = spool.exp_report(cr.dbname, uid, report.report_name,
                                          ids, datas=data, context=context)
            while 1:
                res = spool.exp_report_get(cr.dbname, uid, report_key)
                if res.get('state'):
                    break
                time.sleep(_POLLING_DELAY)
            pdf = base64.b64decode(res.get('result'))
            pdf_reports.append(pdf)
        return pdf_reports

    def _get_report_ids(self, cr, uid, ids, context=None):
        """
        Hook to define the list of report to print
        """
        return []

    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        """Call both report to assemble both pdf"""

        report_ids = self._get_report_ids(cr, uid, ids, context=context)

        pdf_reports = self._generate_all_pdf(cr, uid, ids, data, report_ids, context=context)

        pdf_assemblage = assemble_pdf(pdf_reports)
        return pdf_assemblage, 'pdf'

    def create(self, cr, uid, ids, data, context=None):
        """We override the create function in order to handle generator
           Code taken from report openoffice. Thanks guys :) """
        pool = pooler.get_pool(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cr, uid,
                [('report_name', '=', self.name[7:])], context=context)
        if report_xml_ids:

            report_xml = ir_obj.browse(cr,
                                       uid,
                                       report_xml_ids[0],
                                       context=context)
            report_xml.report_rml = None
            report_xml.report_rml_content = None
            report_xml.report_sxw_content_data = None
            report_xml.report_sxw_content = None
            report_xml.report_sxw = None
        else:
            return super(PDFReportAssembler, self).create(cr, uid, ids, data, context)
        if report_xml.report_type != 'assemblage':
            return super(PDFReportAssembler, self).create(cr, uid, ids, data, context)
        result = self.create_source_pdf(cr, uid, ids, data, report_xml, context)
        if not result:
            return (False, False)
        return result
