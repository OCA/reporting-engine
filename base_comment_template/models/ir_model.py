# Copyright 2020 NextERP Romania SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    is_comment_template = fields.Boolean(
        string="Comment Template",
        default=False,
        help="Whether this model supports in reports to add comment templates.",
    )

    def _reflect_model_params(self, model):
        vals = super()._reflect_model_params(model)
        vals["is_comment_template"] = issubclass(
            type(model), self.pool["comment.template"]
        )
        return vals

    @api.model
    def _instanciate(self, model_data):
        model_class = super()._instanciate(model_data)
        if (
            model_data.get("is_comment_template")
            and model_class._name != "comment.template"
        ):
            parents = model_class._inherit or []
            parents = [parents] if isinstance(parents, str) else parents
            model_class._inherit = parents + ["comment.template"]
        return model_class
