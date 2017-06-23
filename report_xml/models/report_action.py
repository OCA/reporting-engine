# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models
from lxml import etree

_logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report.xml"

    report_type = fields.Selection(selection_add=[("qweb-xml", "XML")])

    def _lookup_report(self, name):
        """Enable ``qweb-xml`` report lookup."""
        try:
            return super(ReportAction, self)._lookup_report(name)
        except Exception as ex:
            # Somebody thought it was a good idea to use standard exceptions
            if "qweb-xml" not in ex.message:
                raise ex
            else:
                self._cr.execute(
                    "SELECT * FROM ir_act_report_xml WHERE report_name=%s",
                    (name,))
                return self._cr.dictfetchone()["report_name"]

    @api.model
    def render_report(self, res_ids, name, data):
        """Special handling for ``qweb-xml`` reports."""
        xml_report = self.search([('report_name', '=', name),
                                  ('report_type', '=', 'qweb-xml')], limit=1)
        if xml_report:
            xml_report = xml_report.ensure_one()
            result = self.env["report"].get_html(res_ids,
                                                 xml_report.report_name,
                                                 data=data)
            return (
                etree.tostring(
                    etree.fromstring(result.strip()),
                    encoding='UTF-8', xml_declaration=True, pretty_print=True
                ), "xml")
        else:
            return super(ReportAction, self).render_report(
                res_ids, name, data)
