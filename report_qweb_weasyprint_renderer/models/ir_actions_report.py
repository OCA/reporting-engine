# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
try:
    from weasyprint import HTML
except ImportError:
    HTML = None


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    qweb_pdf_engine = fields.Selection(
        selection_add=[('weasyprint', 'WeasyPrint')],
    )

    @api.multi
    def _render_qweb_pdf_weasyprint(self, res_ids=None, data=None):
        data = data or {}
        data['enable_editor'] = False,
        context = dict(self.env.context)
        context['qweb_pdf_engine'] = 'weasyprint'

        html = self.with_context(**context).render_qweb_html(
            res_ids, data=data
        )[0]
        return HTML(
            string=html,
            # TODO: pass a custom url fetcher to never actually use the port
            base_url=self.env['ir.config_parameter'].get_param('report.url') or
            self.env['ir.config_parameter'].get_param('web.base.url'),
        ).write_pdf(), 'pdf'
