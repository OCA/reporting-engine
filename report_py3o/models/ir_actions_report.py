# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)

try:
    from py3o.formats import Formats
except ImportError:
    logger.debug('Cannot import py3o.formats')


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

    @api.model
    def get_from_report_name(self, report_name, report_type):
        return self.search(
            [("report_name", "=", report_name),
             ("report_type", "=", report_type)])

    @api.model
    def render_report(self, res_ids, name, data):
        action_py3o_report = self.get_from_report_name(name, "py3o")
        if action_py3o_report:
            return action_py3o_report._render_py3o(res_ids, data)
        return super(IrActionsReport, self).render_report(
            res_ids, name, data)

    @api.multi
    def _render_py3o(self, res_ids, data):
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

    @api.model
    def _get_report_from_name(self, report_name):
        """Get the first record of ir.actions.report having the
        ``report_name`` as value for the field report_name.
        """
        res = super(IrActionsReport, self)._get_report_from_name(report_name)
        if res:
            return res
        # maybe a py3o report
        context = self.env['res.users'].context_get()
        return self.with_context(context).search(
            [('report_type', '=', 'py3o'),
             ('report_name', '=', report_name)], limit=1)

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
