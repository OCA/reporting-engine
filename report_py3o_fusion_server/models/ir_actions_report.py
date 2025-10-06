# © 2013 XCG Consulting <http://odoo.consulting>
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models

logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    py3o_server_id = fields.Many2one("py3o.server", "LibreOffice for Py3o")
    pdf_options_id = fields.Many2one(
        "py3o.pdf.options",
        string="PDF Options",
        ondelete="restrict",
        help="PDF options can be set per report, but also per Py3o Server. "
        "If both are defined, the options on the report are used.",
    )

    @api.depends(
        "lo_bin_path", "is_py3o_native_format", "report_type", "py3o_server_id"
    )
    def _compute_py3o_report_not_available(self):
        for rec in self:
            rec.is_py3o_report_not_available = False
            rec.msg_py3o_report_not_available = ""
            if not rec.report_type == "py3o":
                continue
            if (
                not rec.is_py3o_native_format
                and not rec.lo_bin_path
                and not rec.py3o_server_id
            ):
                rec.is_py3o_report_not_available = True
                rec.msg_py3o_report_not_available = (
                    _(
                        "A fusion server or a libreoffice runtime are required "
                        "to genereate the py3o report '%s'. If the libreoffice"
                        "runtime is already installed and is not found by "
                        "Odoo, you can provide the full path to the runtime by "
                        "setting the key 'py3o.conversion_command' into the "
                        "configuration parameters."
                    )
                    % rec.name
                )
