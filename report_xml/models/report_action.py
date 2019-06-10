# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import api, fields, models
from lxml import etree


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(selection_add=[("qweb-xml", "XML")])

    @api.model
    def render_qweb_xml(self, docids, data=None):
        if not data:
            data = {}
        data.setdefault('report_type', 'text')
        data = self._get_rendering_context(docids, data)
        result = self.render_template(self.report_name, data)
        return etree.tostring(
            etree.fromstring(
                str(result, 'UTF-8').lstrip('\n').lstrip().encode('UTF-8')
            ),
            encoding='UTF-8',
            xml_declaration=True,
            pretty_print=True
        ), "xml"
