# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import logging
from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.safe_eval import safe_eval, time

_logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("fillpdf", "PDF Filler")], ondelete={"fillpdf": "set default"}
    )

    @api.model
    def _render_fillpdf_stream(self, report_ref, docids, data):
        report_sudo = self._get_report(report_ref)
        collected_streams = OrderedDict()

        # Fetch the existing attachments from the database for later use.
        # Reload the stream from the attachment in case of 'attachment_use'.
        if docids:
            records = self.env[report_sudo.model].browse(docids)
            for record in records:
                stream = None
                attachment = None
                if report_sudo.attachment:
                    attachment = report_sudo.retrieve_attachment(record)

                    # If existing attachement, extract the stream from the attachment.
                    if attachment and report_sudo.attachment_use:
                        stream = io.BytesIO(attachment.raw)

                    # If no attachment, generate the pdf
                    else:
                        report_model_name = "report.%s" % self.report_name
                        report_model = self.env.get(report_model_name)
                        if report_model is None:
                            raise UserError(
                                _("%s model was not found") % report_model_name
                            )

                        stream = io.BytesIO(
                            report_model.with_context(
                                **{"active_model": self.model}
                            ).fill_report(docids, data)
                        )
                        _logger.info(
                            "The PDF report has been generated for model: %s, records %s."
                            % (report_model, str(docids))
                        )

                collected_streams[record.id] = {
                    "stream": stream,
                    "attachment": attachment,
                }
        return collected_streams

    @api.model
    def render_fillpdf(self, report_ref, docids, data):
        report_sudo = self._get_report(report_ref)
        collected_streams = self._render_fill_pdf_stream(report_ref, docids, data)

        if report_sudo.attachment:
            attachment_vals_list = []
            for res_id, stream_data in collected_streams.items():
                # An attachment already exists.
                if stream_data["attachment"]:
                    continue

                # if res_id is false
                # we are unable to fetch the record,
                # it won't be saved as we can't split the documents unambiguously
                if not res_id:
                    _logger.warning(
                        "These documents were not saved as an attachment\
                        because the template of %s doesn't "
                        "have any headers seperating different instances\
                        of it. If you want it saved,"
                        "please print the documents separately",
                        report_sudo.report_name,
                    )
                    continue
                record = self.env[report_sudo.model].browse(res_id)
                attachment_name = safe_eval(
                    report_sudo.attachment, {"object": record, "time": time}
                )

                # Unable to compute a name for the attachment.
                if not attachment_name:
                    continue

                attachment_vals_list.append(
                    {
                        "name": attachment_name,
                        "raw": stream_data["stream"].getvalue(),
                        "res_model": report_sudo.model,
                        "res_id": record.id,
                        "type": "binary",
                    }
                )

            if attachment_vals_list:
                attachment_names = ", ".join(x["name"] for x in attachment_vals_list)
                try:
                    self.env["ir.attachment"].create(attachment_vals_list)
                except AccessError:
                    _logger.info(
                        "Cannot save PDF report %r attachments for user %r",
                        attachment_names,
                        self.env.user.display_name,
                    )
                else:
                    _logger.info(
                        "The PDF documents %r are now saved in the database",
                        attachment_names,
                    )

        # Merge all streams together for a single record.
        streams_to_merge = [
            x["stream"] for x in collected_streams.values() if x["stream"]
        ]
        if len(streams_to_merge) == 1:
            pdf_content = streams_to_merge[0].getvalue()
        else:
            with self._merge_pdfs(streams_to_merge) as pdf_merged_stream:
                pdf_content = pdf_merged_stream.getvalue()

        for stream in streams_to_merge:
            stream.close()

        if docids:
            _logger.info(
                "The PDF report has been generated for model: %s, records %s.",
                report_sudo.model,
                str(docids),
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
        return report_obj.with_context(**context).search(conditions, limit=1)
