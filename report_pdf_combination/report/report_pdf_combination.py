# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from cStringIO import StringIO

from odoo import models
from odoo.report.report_sxw import report_sxw
from odoo.api import Environment


import logging
_logger = logging.getLogger(__name__)


try:
    from PyPDF2 import PdfFileMerger
except ImportError:
    _logger.debug('Can not import PyPDF2.PdfFileMerger.')


class ReportPDFCombination(report_sxw):

    def create(self, cr, uid, ids, data, context=None):
        self.env = Environment(cr, uid, context)
        report_obj = self.env['ir.actions.report.xml']
        report = report_obj.search([('report_name', '=', self.name[7:])])
        print ('ReportPDFCombination', report.ids, report.report_type, bool(report.ids), report.report_type == 'pdf-combination')
        if report.ids:
            self.title = report.name
            if report.report_type == 'pdf-combination':
                return self.create_pdf_combination_report(ids, data)
        return super(ReportPDFCombination, self).create(cr, uid, ids, data, context)

    def create_pdf_combination_report(self, docids, data):
        print 'create_pdf_combination_report0 '*10
        objs = self.env[self.env.context.get('active_model')].browse(docids)
        file_list = self.get_files_for_pdf_combination_report(data, objs)
        merger = PdfFileMerger()
        self.configure_merger(merger)

        for f in file_list:
            # for import_bookmarks see https://github.com/mstamy2/PyPDF2/issues/193#issuecomment-248638419
            merger.append(f, import_bookmarks=False)

        file_data = StringIO()
        merger.write(file_data)
        file_data.seek(0)
        print 'create_pdf_combination_report'
        return file_data.read(), 'pdf-combination'

    def configure_merger(self, merger):
        # For posible configurations
        # see https://pythonhosted.org/PyPDF2/PdfFileMerger.html
        pass

    def get_files_for_pdf_combination_report(self, data, objs):
        raise NotImplementedError()

