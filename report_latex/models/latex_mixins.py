# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LatexRecordMixin(models.AbstractModel):
    _name = "latex.record.mixin"
    _description = "Latex Record Mixin"

    res_model_id = fields.Many2one(
        "ir.model",
        "Document Model",
        index=True,
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    res_model = fields.Char(
        "Related Document Model",
        index=True,
        related="res_model_id.model",
        precompute=True,
        store=True,
        readonly=True,
    )
    res_id = fields.Many2oneReference(
        string="Related Document ID", index=True, model_field="res_model"
    )
    reference = fields.Char(compute="_compute_reference")

    @api.depends("res_model", "res_id")
    def _compute_reference(self):
        for rec in self:
            rec.reference = f"{rec.res_model},{rec.res_id}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "res_model" in vals:
                vals["res_model_id"] = self.env["ir.model"]._get(vals["res_model"]).id
        return super().create(vals_list)

    @property
    def record(self):
        self.ensure_one()
        if self.res_model not in self.env:
            return self.env["_unknown"]
        return self.env[self.res_model].browse(self.res_id)
