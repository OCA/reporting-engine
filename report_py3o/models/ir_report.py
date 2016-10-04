# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
from openerp import api, fields, models
from openerp.report.interface import report_int
from ..py3o_parser import Py3oParser
from openerp.exceptions import ValidationError
from openerp import addons


class ReportXml(models.Model):
    """ Inherit from ir.actions.report.xml to allow customizing the template
    file. The user cam chose a template from a list.
    The list is configurable in the configuration tab, see py3o_template.py
    """

    _inherit = 'ir.actions.report.xml'

    @api.one
    @api.constrains("py3o_fusion_filetype", "report_type")
    def _check_py3o_fusion_filetype(self):
        if self.report_type == "py3o" and not self.py3o_fusion_filetype:
            raise ValidationError(
                "Field 'Output Format' is required for Py3O report")

    py3o_fusion_filetype = fields.Many2one(
        'py3o.fusion.filetype',
        "Output Format")
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

    @api.cr
    def _lookup_report(self, cr, name):
        """Look up a report definition.
        """

        # First lookup in the deprecated place, because if the report
        # definition has not been updated, it is more likely the correct
        # definition is there. Only reports with custom parser
        # specified in Python are still there.
        if 'report.' + name in report_int._reports:
            new_report = report_int._reports['report.' + name]
            if not isinstance(new_report, Py3oParser):
                new_report = None
        else:
            cr.execute(
                'SELECT * '
                'FROM ir_act_report_xml '
                'WHERE report_name=%s AND report_type=%s',
                (name, 'py3o')
            )
            r = cr.dictfetchone()
            if r:
                kwargs = {}
                if r['parser']:
                    kwargs['parser'] = getattr(addons, r['parser'])

                new_report = Py3oParser(
                    'report.' + r['report_name'],
                    r['model'],
                    os.path.join('addons', r['report_rml'] or '/'),
                    header=r['header'],
                    register=False,
                    **kwargs
                )
            else:
                new_report = None

        if new_report:
            return new_report
        else:
            return super(ReportXml, self)._lookup_report(cr, name)
