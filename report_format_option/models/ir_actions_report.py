# Copyright 2024 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class IrActionReport(models.Model):
    _inherit = "ir.actions.report"

    encoding = fields.Char(
        help="Encoding to be applied to the generated CSV file. e.g. cp932"
    )
    encode_error_handling = fields.Selection(
        selection=[("ignore", "Ignore"), ("replace", "Replace")],
        help="If nothing is selected, CSV export will fail with an error message when "
        "there is a character that fail to be encoded.",
    )
    show_encoding = fields.Boolean(
        compute="_compute_show_encoding",
        help="Technical field to control the visibility of the encoding field.",
    )
    line_ending = fields.Selection(
        [("crlf", "CRLF (\\r\\n)"), ("cr", "CR (\\r)")],
        help="Select the type of line ending in case the report needs "
        "to be output with other line ending than 'LF'.",
    )
    show_line_ending = fields.Boolean(
        compute="_compute_show_line_ending",
        help="Technical field to control the visibility of the line ending field.",
    )

    def _compute_show_encoding(self):
        """Extend this method to show the encoding field in the report form."""
        for report in self:
            report.show_encoding = False
            if report.report_type == "qweb-text":
                report.show_encoding = True

    def _compute_show_line_ending(self):
        """Extend this method to show the line ending field in the report form."""
        for report in self:
            report.show_line_ending = False
            if report.report_type == "qweb-text":
                report.show_line_ending = True

    @api.model
    def _render_qweb_text(self, report_ref, docids, data=None):
        content, content_type = super()._render_qweb_text(report_ref, docids, data)
        report = self._get_report(report_ref)
        if not report.encoding and not report.line_ending:
            return content, content_type
        content_str = content.decode("utf-8")
        if report.line_ending == "crlf":
            content_str = content_str.replace("\n", "\r\n")
        elif report.line_ending == "cr":
            content_str = content_str.replace("\n", "\r")
        # If specific encoding is set on the report, use it; otherwise, fallback to utf-8
        encoding = report.encoding or "utf-8"
        encode_options = {}
        if report.encode_error_handling:
            encode_options["errors"] = report.encode_error_handling
        content = content_str.encode(encoding, **encode_options)
        return content, content_type
