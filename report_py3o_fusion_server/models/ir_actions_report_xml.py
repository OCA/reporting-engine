# -*- coding: utf-8 -*-
# © 2013 XCG Consulting <http://odoo.consulting>
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import _, api, fields, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

try:
    from py3o.formats import Formats
except ImportError:
    logger.debug('Cannot import py3o.formats')


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    @api.multi
    @api.constrains("py3o_is_local_fusion", "py3o_server_id", "py3o_filetype")
    def _check_py3o_server_id(self):
        for report in self:
            if report.report_type != "py3o":
                continue
            is_native = Formats().get_format(report.py3o_filetype).native
            if ((not is_native or not report.py3o_is_local_fusion) and
                    not report.py3o_server_id):
                raise ValidationError(_(
                    "Can not use not native format in local fusion. "
                    "Please specify a Fusion Server"))

    py3o_is_local_fusion = fields.Boolean(
        "Local Fusion",
        help="Native formats will be processed without a server. "
             "You must use this mode if you call methods on your model into "
             "the template.",
        default=True)
    py3o_server_id = fields.Many2one(
        "py3o.server",
        "Fusion Server")
