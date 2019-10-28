# © 2013 XCG Consulting <http://odoo.consulting>
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.constrains("py3o_is_local_fusion", "py3o_server_id")
    def _check_py3o_server_id(self):
        for report in self:
            if report.report_type != "py3o":
                continue
            if not report.py3o_is_local_fusion and not report.py3o_server_id:
                raise ValidationError(
                    _(
                        "You can not use remote fusion without Fusion server. "
                        "Please specify a Fusion Server"
                    )
                )

    py3o_is_local_fusion = fields.Boolean(
        "Local Fusion",
        help="Native formats will be processed without a server. "
        "You must use this mode if you call methods on your model into "
        "the template.",
        default=True,
    )
    py3o_server_id = fields.Many2one("py3o.server", "Fusion Server")
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
