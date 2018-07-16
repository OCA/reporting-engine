# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from openerp import api, models
from openerp.report import render_report


class MassReportOutput(models.AbstractModel):
    _name = 'mass.report.output'
    _description = "Base model to implement an output format."

    @api.model
    def get_report_types(self):
        """Return the combinations of compatible report types for this output
        format.  If the output format supports all report types, this method
        should return an empty list.
        E.g. an output format able to merge PDF files *or* Excel files together
        (but not PDF *and* Excel) could return the following:

            return [
                ['qweb-pdf', 'pdf'],
                ['xlsx'],
            ]
        """
        raise NotImplementedError

    @api.model
    def _process_report_attachment(self, report_attachment):
        """Generate a report and store it as an attachment."""
        record = report_attachment.record_id
        report = report_attachment.report_id
        content, format_ = render_report(
            self.env.cr,
            report_attachment.mass_report_id.user_id.id,
            record.ids,
            report.report_name,
            data={'model': record._name},
            context=self.env.context)
        name = "%s_%s" % (report.name, record.id)
        file_name = "%s.%s" % (name, format_)
        vals = {
            'name': name,
            'datas': base64.encodestring(content),
            'datas_fname': file_name,
            'res_model': report_attachment._name,
            'res_id': report_attachment.id,
        }
        attachment = self.env['ir.attachment'].create(vals)
        report_attachment.attachment_id = attachment
        return True

    @api.model
    def process_mass_report(self, mass_report_id):
        """Build the final report's output from attachments."""
        raise NotImplementedError
