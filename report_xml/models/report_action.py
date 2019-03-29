# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import logging

from odoo import api, fields, models
from lxml import etree

_logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(selection_add=[("qweb-xml", "XML")])

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report']
        qwebtypes = ['qweb-xml']
        conditions = [('report_type', 'in', qwebtypes),
                      ('report_name', '=', report_name)]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)

    @api.model
    def render_qweb_xml(self, docids, data):
        result = self.render_qweb_html(docids, data=data)
        return etree.tostring(
            etree.fromstring(
                str(result[0], 'UTF-8').lstrip('\n').lstrip().encode('UTF-8')
            ),
            encoding='UTF-8',
            xml_declaration=True,
            pretty_print=True
        ), "xml"
