# Copyright 2024 Quartile Limited (https://www.quartile.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class FloatConverter(models.AbstractModel):
    _inherit = "ir.qweb.field.float"

    @api.model
    def record_to_html(self, record, field_name, options):
        if "precision" not in options and "decimal_precision" not in options:
            qweb_recs = self.env["qweb.field.converter"].search(
                [("res_model_name", "=", record._name), ("field_name", "=", field_name)]
            )
            precision_rec = max(
                qweb_recs, default=None, key=lambda r: r._get_score(record)
            )
            if precision_rec:
                options = dict(options, precision=precision_rec.digits)
        return super().record_to_html(record, field_name, options)
