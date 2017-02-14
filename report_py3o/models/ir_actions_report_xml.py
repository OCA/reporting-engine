# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

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

    @api.one
    @api.constrains("py3o_filetype", "report_type")
    def _check_py3o_filetype(self):
        if self.report_type == "py3o" and not self.py3o_filetype:
            raise ValidationError(_(
                "Field 'Output Format' is required for Py3O report"))

    @api.one
    @api.constrains("py3o_is_local_fusion", "py3o_server_id",
                    "py3o_filetype")
    def _check_py3o_server_id(self):
        if self.report_type != "py3o":
            return
        is_native = Formats().get_format(self.py3o_filetype).native
        if ((not is_native or not self.py3o_is_local_fusion) and
                not self.py3o_server_id):
            raise ValidationError(_(
                "Can not use not native format in local fusion. "
                "Please specify a Fusion Server"))

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
    py3o_is_local_fusion = fields.Boolean(
        "Local Fusion",
        help="Native formats will be processed without a server. "
             "You must use this mode if you call methods on your model into "
             "the template.",
        default=True)
    py3o_server_id = fields.Many2one(
        "py3o.server",
        "Fusion Server")
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

    @api.model
    def render_report(self, res_ids, name, data):
        action_py3o_report = self.search(
            [("report_name", "=", name),
             ("report_type", "=", "py3o")])
        if action_py3o_report:
            return self.env['py3o.report'].create({
                'ir_actions_report_xml_id': action_py3o_report.id
            }).create_report(res_ids, data)
        return super(IrActionsReportXml, self).render_report(
            res_ids, name, data)
