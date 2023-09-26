# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.safe_eval import safe_eval, time

_logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("csv", "csv")], ondelete={"csv": "set default"}
    )
    encoding = fields.Char(
        help="Encoding to be applied to the generated CSV file. e.g. cp932"
    )
    encode_error_handling = fields.Selection(
        selection=[("ignore", "Ignore"), ("replace", "Replace")],
        help="If nothing is selected, CSV export will fail with an error message when "
        "there is a character that fail to be encoded.",
    )

    def _create_csv_attachment(self, record, data):
        attachment_name = safe_eval(self.attachment, {"object": record, "time": time})
        # Unable to compute a name for the attachment.
        if not attachment_name:
            return
        if record and data:
            attachment = {
                "name": attachment_name,
                "raw": data,
                "res_model": self.model,
                "res_id": record.id,
                "type": "binary",
            }
            try:
                self.env["ir.attachment"].create(attachment)
            except AccessError:
                _logger.info(
                    "Cannot save csv report %r as attachment", attachment["name"]
                )
            else:
                _logger.info(
                    "The csv document %s is now saved in the database",
                    attachment["name"],
                )

    @api.model
    def _render_csv(self, report_ref, docids, data):
        report_sudo = self._get_report(report_ref)
        report_model_name = "report.%s" % report_sudo.report_name
        report_model = self.env[report_model_name]
        res_id = len(docids) == 1 and docids[0]
        if not res_id or not report_sudo.attachment or not report_sudo.attachment_use:
            return report_model.with_context(
                **{
                    "active_model": report_sudo.model,
                    "encoding": self.encoding,
                    "encode_error_handling": self.encode_error_handling,
                }
            ).create_csv_report(docids, data)
        record = self.env[report_sudo.model].browse(res_id)
        attachment = report_sudo.retrieve_attachment(record)
        if attachment:
            return attachment.raw.decode(), "csv"
        data, ext = report_model.with_context(
            **{
                "active_model": report_sudo.model,
                "encoding": self.encoding,
                "encode_error_handling": self.encode_error_handling,
            }
        ).create_csv_report(docids, data)
        report_sudo._create_csv_attachment(record, data)
        return data, ext

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["csv"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(**context).search(conditions, limit=1)
