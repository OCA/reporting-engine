# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class IrActionsReport(models.Model):

    _inherit = "ir.actions.report"

    code_data = fields.Text()

    def _get_code_data_input_dict(self, res_ids, data):
        Model = self.env[self.model]
        records = Model.browse(res_ids)
        return {
            "records": records,
            "self": self,
        }

    def render(self, res_ids, data=None):
        if not data:
            data = {}
        if self.code_data:
            results = self._get_code_data_input_dict(res_ids, data)
            safe_eval(self.code_data, results, mode="exec", nocopy=True)
            data.update(results.get("result", {}))
        return super(IrActionsReport, self).render(res_ids, data=data)
