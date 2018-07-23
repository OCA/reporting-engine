# Copyright 2017 Akretion (http://www.akretion.com/)
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
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


class ReportAction(models.Model):

    _inherit = 'ir.actions.report'

    report_type = fields.Selection(selection_add=[("py3o", "py3o")])
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

    py3o_multi_in_one = fields.Boolean(
        string='Multiple Records in a Single Report',
        help="If you execute a report on several records, "
             "by default Odoo will generate a ZIP file that contains as many "
             "files as selected records. If you enable this option, Odoo will"
             "generate instead a single report for the selected records.")

    @api.model
    def render_py3o(self, docids, data):
        return self.env['py3o.report'].create(
            {'ir_actions_report_id': self.id}).create_report(docids, data)

    @api.model
    def _get_report_from_name(self, report_name):
        """Get the first record of ir.actions.report having the
        ``report_name`` as value for the field report_name.
        """
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        # maybe a py3o report
        report_obj = self.env['ir.actions.report']
        qwebtypes = ['py3o']
        conditions = [('report_type', 'in', qwebtypes),
                      ('report_name', '=', report_name)]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)

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

    @api.multi
    def gen_report_download_filename(self, res_ids, data):
        """Override this function to change the name of the downloaded report
        """
        self.ensure_one()
        object_name = self.env[self.model].search(
            [('id', 'in', res_ids)]).name
        report = self._get_report_from_name(self.report_name)
        if report.print_report_name and not len(res_ids) > 1:
            obj = self.env[self.model].browse(res_ids)
            return safe_eval(report.print_report_name,
                             {'object': obj, 'time': time})
        return "%s.%s" % (object_name, self.py3o_filetype)

    @api.multi
    def unlink(self):
        for record in self:
            self.env['py3o.report'].search(
                [('ir_actions_report_id', '=', record.id)]).unlink()

        return super(ReportAction, self).unlink()
