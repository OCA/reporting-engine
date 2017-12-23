# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.modules import get_resource_path


class PartnerPDF(models.AbstractModel):
    _name = 'report.report_fillpdf.partner_fillpdf'
    _inherit = 'report.report_fillpdf.abstract'

    @api.model
    def get_original_document_path(self, data, objs):
        return get_resource_path(
            'report_fillpdf', 'static/src/pdf', 'partner_pdf.pdf')

    @api.model
    def get_document_values(self, data, objs):
        objs.ensure_one()
        return {'name': objs.name}
