# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
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


class IrActionsReportXml(models.Model):
    """ Inherit from ir.actions.report.xml to allow customizing the template
    file. The user cam chose a template from a list.
    The list is configurable in the configuration tab, see py3o_template.py
    """

    _inherit = 'ir.actions.report.xml'

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
            return self.env['py3o.report'].create({
                'ir_actions_report_xml_id': action_py3o_report.id
            }).create_report(res_ids, data)
        return super(IrActionsReportXml, self).render_report(
            res_ids, name, data)

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
