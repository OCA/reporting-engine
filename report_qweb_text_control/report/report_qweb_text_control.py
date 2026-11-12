# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re

from odoo import api, fields, models

from . import field_formatter


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    text_control_enabled = fields.Boolean(
        string="Enable Text Control",
        help="Enable whitespace control and field formatting for text reports",
    )

    @api.model
    def _get_rendering_context(self, report, docids, data):
        # Add field formatters to rendering context only when text control is enabled
        context = super()._get_rendering_context(report, docids, data)
        if report.text_control_enabled:
            context.update(
                {
                    "A": field_formatter.A,
                    "N": field_formatter.N,
                    "M": field_formatter.M,
                    "T": field_formatter.T,
                    "D": field_formatter.D,
                    "DT": field_formatter.DT,
                    "H": field_formatter.H,
                }
            )
        return context

    @api.model
    def _render_qweb_text(self, report_ref, docids, data=None):
        # Extend text rendering with post-processing when text control is enabled
        content, format_type = super()._render_qweb_text(report_ref, docids, data=data)
        report = self._get_report(report_ref)
        if report.text_control_enabled:
            is_bytes = isinstance(content, bytes)
            processed_content = report._postprocess_text(content)
            content = processed_content.encode() if is_bytes else processed_content
        return content, format_type

    def _postprocess_text(self, content):
        """Post-process text content to control whitespace and replace elements."""
        # Ensure content is a string (decode if bytes)
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        # Strip spaces from each line first
        lines = content.split("\n")
        stripped_lines = [line.strip() for line in lines]
        content = "\n".join(stripped_lines)

        # Remove all unwanted line breaks (both \r and \n) first
        content = re.sub(r"[\r\n]+", "", content)

        # Then replace special elements with their corresponding characters
        replacement_elements = self._get_replacement_elements()
        for element, replacement in replacement_elements.items():
            # Replace opening tags with the replacement character
            pattern = (
                f"<{element}>|<{element}/>|<{element.lower()}>|<{element.lower()}/>"
            )
            content = re.sub(pattern, replacement, content)
            # Remove closing tags completely
            pattern_close = f"</{element}>|</{element.lower()}>"
            content = re.sub(pattern_close, "", content)

        return content

    def _get_replacement_elements(self):
        """Return dictionary of special elements and their replacements."""
        return {
            "CR": "\r",
            "LF": "\n",
            "CRLF": "\r\n",
            "TAB": "\t",
            "PIPE": "|",
            "SEMICOLON": ";",
            "SPAN": "",
            "DIV": "",
        }
