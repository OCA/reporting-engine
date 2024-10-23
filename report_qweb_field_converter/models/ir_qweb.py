# Copyright 2024 Quartile Limited (https://www.quartile.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrQweb(models.AbstractModel):
    _inherit = "ir.qweb"

    @api.model
    def _get_field(
        self, record, field_name, expression, tagName, field_options, values
    ):
        report_type = values.get("report_type")
        if not report_type or report_type != "pdf":
            return super()._get_field(
                record, field_name, expression, tagName, field_options, values
            )
        qweb_recs = self.env["qweb.field.converter"].search(
            [("res_model_name", "=", record._name), ("field_name", "=", field_name)]
        )
        options_rec = max(qweb_recs, default=None, key=lambda r: r._get_score(record))
        if options_rec and options_rec.field_options:
            try:
                additional_options = json.loads(options_rec.field_options)
                field_options.update(additional_options)
            except json.JSONDecodeError as e:
                _logger.error(f"JSON decoding error for field options: {e}")
        return super()._get_field(
            record, field_name, expression, tagName, field_options, values
        )
