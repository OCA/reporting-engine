# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
from StringIO import StringIO
import zipfile

from openerp import api, models


class MassReportOutputZipFiles(models.AbstractModel):
    # pylint: disable=consider-merging-classes-inherited
    _inherit = 'mass.report.output'
    _name = 'mass.report.output.zip_files'
    _description = "ZIP - Archive with one file per report"

    @api.model
    def get_report_types(self):
        return []

    @api.model
    def process_mass_report(self, mass_report_id):
        mass_report = self.env['mass.report'].browse(mass_report_id)
        file_ = StringIO()
        with zipfile.ZipFile(file_, mode='w') as output:
            for ra in mass_report.report_attachment_ids:
                if not ra.attachment_id:
                    continue
                content_b64 = ra.attachment_id.datas
                content = base64.decodestring(content_b64)
                output.writestr(ra.attachment_id.datas_fname, content)
        file_name = "%s.%s" % (mass_report.name, 'zip')
        file_.seek(0)
        vals = {
            'name': file_name,
            'datas': base64.encodestring(file_.getvalue()),
            'datas_fname': file_name,
            'res_model': mass_report._name,
            'res_id': mass_report.id,
        }
        mass_report.output_file = self.env['ir.attachment'].create(vals)
        return True
