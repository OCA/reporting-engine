# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(selection_add=[("excel", "Excel")])

    @api.model
    def render_excel(self, docids, data):
        if len(docids) != 1:
            raise UserError(_('Only one id is allowed for export_xlsx'))
        xlsx_template = self.env['xlsx.template'].search(
            [('fname', '=', self.report_name), ('res_model', '=', self.model)])
        if not xlsx_template:
            raise UserError(
                _("Template %s on model %s was not found" %
                  (self.report_name, self.model)))
        Export = self.env['xlsx.export']
        return Export.export_xlsx(xlsx_template, self.model, docids[0])

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report']
        qwebtypes = ['excel']
        conditions = [
            ('report_type', 'in', qwebtypes),
            ('report_name', '=', report_name),
        ]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)
