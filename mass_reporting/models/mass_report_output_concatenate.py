# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import base64
from StringIO import StringIO

from openerp import api, models

_logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError:
    _logger.debug('Can not import PyPDF2')


class MassReportOutputConcatenate(models.AbstractModel):
    # pylint: disable=consider-merging-classes-inherited
    _inherit = 'mass.report.output'
    _name = 'mass.report.output.concatenate'
    _description = "One file - Concatenate reports into one"

    @api.model
    def get_report_types(self):
        return [
            ['qweb-pdf', 'pdf'],
        ]

    @api.model
    def process_mass_report(self, mass_report_id):
        mass_report = self.env['mass.report'].browse(mass_report_id)
        output = PdfFileWriter()
        for ra in mass_report.report_attachment_ids:
            if not ra.attachment_id:
                continue
            content_b64 = ra.attachment_id.datas
            content = base64.decodestring(content_b64)
            reader = PdfFileReader(StringIO(content))
            for page in range(reader.getNumPages()):
                output.addPage(reader.getPage(page))
        output_file = StringIO()
        output.write(output_file)
        file_name = "%s.%s" % (mass_report.name, 'pdf')
        vals = {
            'name': file_name,
            'datas': base64.encodestring(output_file.getvalue()),
            'datas_fname': file_name,
            'res_model': mass_report._name,
            'res_id': mass_report.id,
        }
        mass_report.output_file = self.env['ir.attachment'].create(vals)
        return True
