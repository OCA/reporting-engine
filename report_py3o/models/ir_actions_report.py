# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import find_in_path
from odoo.tools.safe_eval import safe_eval


logger = logging.getLogger(__name__)

try:
    from py3o.formats import Formats
except ImportError:
    logger.debug('Cannot import py3o.formats')

PY3O_CONVERSION_COMMAND_PARAMETER = "py3o.conversion_command"


class IrActionsReport(models.Model):
    """ Inherit from ir.actions.report to allow customizing the template
    file. The user cam chose a template from a list.
    The list is configurable in the configuration tab, see py3o_template.py
    """

    _inherit = 'ir.actions.report'

    @api.multi
    @api.constrains("py3o_filetype", "report_type")
    def _check_py3o_filetype(self):
        for report in self:
            if report.report_type == "py3o" and not report.py3o_filetype:
                raise ValidationError(_(
                    "Field 'Output Format' is required for Py3O report"))

    @api.model
    def _get_py3o_filetypes(self):
        formats = Formats()
        names = formats.get_known_format_names()
        selections = []
        for name in names:
            description = name
            if formats.get_format(name).native:
                description = description + " " + _("(Native)")
            selections.append((name, description))
        return selections

    report_type = fields.Selection(
        selection_add=[("py3o", "py3o")]
        )
    py3o_filetype = fields.Selection(
        selection="_get_py3o_filetypes",
        string="Output Format")
    is_py3o_native_format = fields.Boolean(
        compute='_compute_is_py3o_native_format'
    )
    py3o_template_id = fields.Many2one(
        'py3o.template',
        "Template")
    module = fields.Char(
        "Module",
        help="The implementer module that provides this report")
    py3o_template_fallback = fields.Char(
        "Fallback",
        size=128,
        help=(
            "If the user does not provide a template this will be used "
            "it should be a relative path to root of YOUR module "
            "or an absolute path on your server."
        ))
    report_type = fields.Selection(selection_add=[('py3o', "Py3o")])
    py3o_multi_in_one = fields.Boolean(
        string='Multiple Records in a Single Report',
        help="If you execute a report on several records, "
        "by default Odoo will generate a ZIP file that contains as many "
        "files as selected records. If you enable this option, Odoo will "
        "generate instead a single report for the selected records.")
    lo_bin_path = fields.Char(
        string="Path to the libreoffice runtime",
        compute="_compute_lo_bin_path"
        )
    is_py3o_report_not_available = fields.Boolean(
        compute='_compute_py3o_report_not_available'
        )
    msg_py3o_report_not_available = fields.Char(
        compute='_compute_py3o_report_not_available'
        )

    @api.model
    def _register_hook(self):
        self._validate_reports()

    @api.model
    def _validate_reports(self):
        """Check if the existing py3o reports should work with the current
        installation.

        This method log a warning message into the logs for each report
        that should not work.
        """
        for report in self.search([("report_type", "=", "py3o")]):
            if report.is_py3o_report_not_available:
                logger.warning(report.msg_py3o_report_not_available)

    @api.model
    def _get_lo_bin(self):
        lo_bin = self.env['ir.config_parameter'].sudo().get_param(
            PY3O_CONVERSION_COMMAND_PARAMETER, 'libreoffice',
        )
        try:
            lo_bin = find_in_path(lo_bin)
        except IOError:
            lo_bin = None
        return lo_bin

    @api.depends("report_type", "py3o_filetype")
    @api.multi
    def _compute_is_py3o_native_format(self):
        format = Formats()
        for rec in self:
            if not rec.report_type == "py3o":
                continue
            filetype = rec.py3o_filetype
            rec.is_py3o_native_format = format.get_format(filetype).native

    @api.multi
    def _compute_lo_bin_path(self):
        lo_bin = self._get_lo_bin()
        for rec in self:
            rec.lo_bin_path = lo_bin

    @api.depends("lo_bin_path", "is_py3o_native_format", "report_type")
    @api.multi
    def _compute_py3o_report_not_available(self):
        for rec in self:
            if not rec.report_type == "py3o":
                continue
            if not rec.is_py3o_native_format and not rec.lo_bin_path:
                rec.is_py3o_report_not_available = True
                rec.msg_py3o_report_not_available = _(
                    "The libreoffice runtime is required to genereate the "
                    "py3o report '%s' but is not found into the bin path. You "
                    "must install the libreoffice runtime on the server. If "
                    "the runtime is already installed and is not found by "
                    "Odoo, you can provide the full path to the runtime by "
                    "setting the key 'py3o.conversion_command' into the "
                    "configuration parameters."
                ) % rec.name

    @api.model
    def get_from_report_name(self, report_name, report_type):
        return self.search(
            [("report_name", "=", report_name),
             ("report_type", "=", report_type)])

    @api.multi
    def render_py3o(self, res_ids, data):
        self.ensure_one()
        if self.report_type != "py3o":
            raise RuntimeError(
                "py3o rendition is only available on py3o report.\n"
                "(current: '{}', expected 'py3o'".format(self.report_type))
        return self.env['py3o.report'].create({
            'ir_actions_report_id': self.id
        }).create_report(res_ids, data)

    @api.multi
    def gen_report_download_filename(self, res_ids, data):
        """Override this function to change the name of the downloaded report
        """
        self.ensure_one()
        report = self.get_from_report_name(self.report_name, self.report_type)
        if report.print_report_name and not len(res_ids) > 1:
            obj = self.env[self.model].browse(res_ids)
            return safe_eval(report.print_report_name,
                             {'object': obj, 'time': time})
        return "%s.%s" % (self.name, self.py3o_filetype)

    @api.multi
    def _get_attachments(self, res_ids):
        """ Return the report already generated for the given res_ids
        """
        self.ensure_one()
        save_in_attachment = {}
        if res_ids:
            # Dispatch the records by ones having an attachment
            Model = self.env[self.model]
            record_ids = Model.browse(res_ids)
            if self.attachment:
                for record_id in record_ids:
                    attachment_id = self.retrieve_attachment(record_id)
                    if attachment_id:
                        save_in_attachment[record_id.id] = attachment_id
        return save_in_attachment
