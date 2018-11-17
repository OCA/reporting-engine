# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    qweb_pdf_engine = fields.Selection(
        [('wkhtmltopdf', 'wkhtmltopdf')], default='wkhtmltopdf',
        string='PDF Engine',
    )

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        if self.qweb_pdf_engine == 'wkhtmltopdf':
            return super(IrActionsReport, self).render_qweb_pdf(
                res_ids=res_ids, data=data,
            )
        return getattr(self, '_render_qweb_pdf_%s' % self.qweb_pdf_engine)(
            res_ids=res_ids, data=data,
        )
