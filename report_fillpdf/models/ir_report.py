# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("fillpdf", "PDF Filler")], ondelete={"fillpdf": "set default"}
    )

    @api.model
    def render_fillpdf(self, docids, data):
        # Here we add pdf attachment support
        self_sudo = self.sudo()
        save_in_attachment = OrderedDict()
        # Maps the streams in `save_in_attachment` back to the records they came from
        stream_record = dict()
        if docids:
            # Dispatch the records by ones having an attachment and ones requesting a call to
            # fillpdf.
            Model = self.env[self_sudo.model]
            record_ids = Model.browse(docids)
            fp_record_ids = Model
            if self_sudo.attachment:
                for record_id in record_ids:
                    attachment = self_sudo.retrieve_attachment(record_id)
                    if attachment:
                        stream = self_sudo._retrieve_stream_from_attachment(attachment)
                        save_in_attachment[record_id.id] = stream
                        stream_record[stream] = record_id
                    if not self_sudo.attachment_use or not attachment:
                        fp_record_ids += record_id

            else:
                fp_record_ids = record_ids
            docids = fp_record_ids.ids

        if save_in_attachment and not docids:
            _logger.info("The PDF report has been generated from attachments.")
            self._raise_on_unreadable_pdfs(save_in_attachment.values(), stream_record)
            return self_sudo._post_pdf(save_in_attachment), "pdf"

        # We generate pdf with fillpdf
        report_model_name = "report.%s" % self.report_name
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_("%s model was not found" % report_model_name))

        pdf_content = report_model.with_context(
            {"active_model": self.model}
        ).fill_report(docids, data)

        if docids:
            self._raise_on_unreadable_pdfs(save_in_attachment.values(), stream_record)
            _logger.info(
                "The PDF report has been generated for model: %s, records %s."
                % (self_sudo.model, str(docids))
            )
            return (
                self_sudo._post_pdf(
                    save_in_attachment, pdf_content=pdf_content, res_ids=docids
                ),
                "pdf",
            )

        return pdf_content, "pdf"

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["fillpdf"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)
