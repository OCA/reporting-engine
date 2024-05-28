# Copyright 2024 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class IrActionReport(models.Model):
    _inherit = "ir.actions.report"

    text_encoding = fields.Char(
        help="Encoding to be applied to the generated Text file. e.g. cp932"
    )
    text_encode_error_handling = fields.Selection(
        selection=[("ignore", "Ignore"), ("replace", "Replace")],
        help="If nothing is selected, text export will fail with an error message when "
        "there is a character that fail to be encoded.",
    )
    line_ending = fields.Selection(
        [("crlf", "CRLF (\\r\\n)"), ("cr", "CR (\\r)")],
        help="Select the type of line ending in case the report needs "
        "to be output with other line ending than 'LF'.",
    )

    @api.model
    def _render_qweb_text(self, report_ref, docids, data=None):
        content, content_type = super()._render_qweb_text(report_ref, docids, data)
        report = self._get_report(report_ref)
        if not report.text_encoding and not report.line_ending:
            return content, content_type
        content_str = content.decode("utf-8")
        if report.line_ending == "crlf":
            content_str = content_str.replace("\n", "\r\n")
        elif report.line_ending == "cr":
            content_str = content_str.replace("\n", "\r")
        # If specific encoding is set on the report, use it; otherwise, fallback to utf-8
        encoding = report.text_encoding or "utf-8"
        encode_options = {}
        if report.text_encode_error_handling:
            encode_options["errors"] = report.text_encode_error_handling
        content = content_str.encode(encoding, **encode_options)
        return content, content_type
