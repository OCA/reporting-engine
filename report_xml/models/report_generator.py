# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ReportGenerator(models.Model):
    _inherit = "report"

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportGenerator, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report.xml']
        qwebtypes = ['qweb-xml']
        conditions = [('report_type', 'in', qwebtypes),
                      ('report_name', '=', report_name)]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)
